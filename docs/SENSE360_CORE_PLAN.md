# Sense360 Core Board & Expansion Module Plan

**Created**: 2025-12-04
**Status**: Planning Phase
**Version**: 1.0.0

---

## Executive Summary

This document outlines the architecture and implementation plan for the Sense360 Core board family and its modular expansion system. The design enables a flexible, scalable platform where a core board provides connectivity and power, while expansion modules add specific functionality.

---

## 1. Architecture Overview

### 1.1 Design Philosophy

**Modular System Design:**
- **Core Board**: Provides ESP32, power management, connectivity (WiFi/BT/PoE), and expansion bus
- **Expansion Modules**: Add sensors and actuators via standardized I2C/UART/GPIO interfaces
- **Power Flexibility**: Support for 240V AC, PoE (IEEE 802.3af), and USB-C (5V)
- **Software Modularity**: YAML packages for mix-and-match configuration

### 1.2 System Layers

```
┌─────────────────────────────────────────────┐
│         User Configuration Layer            │
│    (products/*.yaml - complete devices)     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Feature Profile Layer                │
│  (packages/features/*_profile.yaml)         │
│  Basic vs Advanced, LED patterns, etc.      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       Expansion Module Layer                │
│  (packages/expansions/*.yaml)               │
│  Sensor drivers, actuator control           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Core Board Layer                   │
│  (packages/hardware/sense360_core_*.yaml)   │
│  ESP32, power, I2C, UART, GPIO config       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Base System Layer                   │
│  (packages/base/*.yaml)                     │
│  WiFi, API, OTA, Time, Logging, BT Proxy   │
└─────────────────────────────────────────────┘
```

---

## 2. Core Board Variants

### 2.1 Sense360 Core (Standard)

**Target Use Case**: General-purpose smart home device, modular expansion platform

**Hardware Specifications:**
- **MCU**: ESP32-S3-WROOM-1 (8MB Flash, 2MB PSRAM)
- **Connectivity**: WiFi 2.4GHz, Bluetooth 5.0 LE
- **Power Input**:
  - 240V AC (via onboard AC-DC converter, 5V/2A output)
  - PoE (IEEE 802.3af, Class 0, 12.95W max)
  - USB-C (5V/2A, PD negotiation optional)
- **Expansion Bus**:
  - Primary I2C (GPIO39/40, 3.3V, 400kHz)
  - Secondary I2C (GPIO21/18, 3.3V, 400kHz) - optional
  - UART (GPIO1/2, 3.3V, configurable baud)
  - GPIO expansion (4x configurable pins: GPIO4, GPIO5, GPIO6, GPIO7)
  - Power rails: 5V (1A), 3.3V (500mA)
- **Status Indicators**:
  - RGB LED (WS2812B or similar) on GPIO48
  - Status LED (GPIO2)
- **Buttons**:
  - Reset/Boot button (GPIO0)
  - User button (GPIO9)
- **Relay**: Optional GPIO relay (GPIO10, 10A AC/DC)

**File**: `packages/hardware/sense360_core.yaml`

---

### 2.2 Sense360 Core Voice

**Target Use Case**: Voice-controlled smart home hub with expansion modules

**Hardware Specifications:**
- **Base**: Same as Sense360 Core (Standard)
- **Additional Features**:
  - **Microphone**: I2S MEMS microphone (INMP441 or similar)
    - I2S pins: GPIO11 (SCK), GPIO12 (WS), GPIO13 (SD)
  - **Speaker/Audio Out**: I2S DAC (MAX98357A or similar)
    - I2S pins: GPIO14 (BCLK), GPIO15 (LRC), GPIO16 (DIN)
    - Amplifier: 3W Class D
  - **Wake Word**: Local wake word detection (ESPHome voice assistant)
  - **Audio Processing**: Optional noise cancellation, AEC
- **Power Requirements**: Higher due to audio (recommend PoE or 240V AC)

**File**: `packages/hardware/sense360_core_voice.yaml`

---

### 2.3 Power Management Architecture

**Power Selection Priority:**
1. **PoE** (if connected) - provides most stable power
2. **240V AC** (if connected) - secondary option
3. **USB-C** (fallback) - lowest priority

**Power Distribution:**
```
┌────────────────────────────────────────────┐
│  Input: 240V AC / PoE / USB-C              │
└──────────────┬─────────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│  Power Management IC (TPS2561, or similar) │
│  - Overvoltage protection                  │
│  - Overcurrent protection                  │
│  - Reverse polarity protection             │
└──────────────┬─────────────────────────────┘
               ↓
       ┌───────┴───────┐
       ↓               ↓
┌──────────┐    ┌──────────┐
│ 5V Rail  │    │ 3.3V Rail│
│ (2A max) │    │ (1A max) │
└────┬─────┘    └────┬─────┘
     ↓               ↓
┌────────────────────────┐
│  ESP32-S3 + Peripherals│
│  Expansion Modules     │
└────────────────────────┘
```

**Files**:
- `packages/hardware/power_240v.yaml` - AC power configuration
- `packages/hardware/power_poe.yaml` - PoE configuration
- `packages/hardware/power_usb.yaml` - USB-C configuration
- `packages/features/power_monitoring.yaml` - Power consumption tracking

---

## 3. Expansion Modules

### 3.1 Module Architecture

**Standardized Interface:**
- **Connector**: 10-pin header (2x5, 2.54mm pitch) or FPC connector
- **Pinout**:
  1. GND
  2. 3.3V
  3. 5V
  4. I2C SDA
  5. I2C SCL
  6. UART TX
  7. UART RX
  8. GPIO1
  9. GPIO2
  10. IRQ (optional)

**Module Identification:**
- Each module has a unique I2C address range
- Software auto-detection via I2C scan
- Configuration via YAML packages

---

### 3.2 Sense360 AirIQ Module

**Purpose**: Comprehensive air quality monitoring

**Sensors:**
- **SEN55** (Sensirion): PM1.0, PM2.5, PM4.0, PM10, VOC, NOx, Temp, Humidity
  - I2C Address: 0x69
- **SCD41** (Sensirion): CO2, Temperature, Humidity
  - I2C Address: 0x62
- **Optional SHT30**: Backup temperature/humidity sensor
  - I2C Address: 0x44

**Features:**
- Real-time air quality index (AQI) calculation
- CO2 concentration monitoring (400-5000 ppm)
- Particulate matter detection
- VOC index (1-500)
- Temperature compensation
- Automatic baseline calibration

**Files:**
- `packages/expansions/airiq.yaml` - Hardware driver
- `packages/features/airiq_basic_profile.yaml` - User-facing entities
- `packages/features/airiq_advanced_profile.yaml` - Technical entities

**Products Using This Module:**
- Sense360 Core + AirIQ
- Sense360 Core Voice + AirIQ
- Sense360 Bathroom (variant with different sensors)

---

### 3.3 Sense360 Comfort Module

**Purpose**: Environmental comfort monitoring and control

**Sensors:**
- **SHT40** (Sensirion): High-accuracy temperature and humidity
  - I2C Address: 0x44
- **BH1750** (ROHM): Ambient light sensor (lux)
  - I2C Address: 0x23
- **BME680** (Bosch, optional): Pressure, gas resistance (IAQ)
  - I2C Address: 0x76

**Actuators (Optional):**
- **Relay Output**: Control HVAC, humidifier, dehumidifier (via core board relay)
- **PWM Output**: Fan speed control

**Features:**
- Comfort index calculation (based on temp, humidity, light)
- Dew point calculation
- Heat index / feels-like temperature
- Circadian lighting recommendations
- HVAC automation triggers

**Files:**
- `packages/expansions/comfort.yaml` - Hardware driver
- `packages/features/comfort_basic_profile.yaml` - User-facing entities
- `packages/features/comfort_advanced_profile.yaml` - Technical entities

**Products Using This Module:**
- Sense360 Core + Comfort
- Sense360 Core Voice + Comfort

---

### 3.4 Sense360 Presence Module

**Purpose**: Human presence detection and tracking

**Sensors:**
- **LD2450** (HLK): 24GHz mmWave radar, multi-target tracking
  - UART interface (TX: GPIO1, RX: GPIO2, 256000 baud)
  - Up to 3 simultaneous targets
  - Zone configuration support
- **LD2412** (HLK): 24GHz mmWave radar, single-zone detection
  - UART interface (TX: GPIO1, RX: GPIO2, 115200 baud)
  - Simpler configuration, lower cost alternative

**Features:**
- Real-time presence detection
- Multi-zone tracking (LD2450)
- Static vs moving target differentiation
- Configurable detection zones
- Presence timeout customization
- Integration with lighting/HVAC automation

**Files:**
- `packages/expansions/presence_ld2450.yaml` - LD2450 driver (already exists: `packages/hardware/presence_ld2450.yaml`)
- `packages/expansions/presence_ld2412.yaml` - LD2412 driver (already exists: `packages/hardware/presence_ld2412.yaml`)
- `packages/features/presence_basic_profile.yaml` - User-facing entities (already exists)
- `packages/features/presence_advanced_profile.yaml` - Technical entities (already exists)

**Products Using This Module:**
- Sense360 Core + Presence (LD2450 or LD2412)
- Sense360 Core Voice + Presence
- Sense360 Mini + Presence (already implemented)

---

### 3.5 Sense360 Fan Module

**Purpose**: Fan speed control with multiple driver options

**Two Variants:**

#### 3.5.1 Fan Module - PWM Version
**Actuators:**
- **PWM Output**: Direct PWM control (GPIO4, 5V tolerant)
  - Frequency: 25kHz (standard PC fan PWM)
  - Duty cycle: 0-100%
- **Tachometer Input**: Fan speed feedback (GPIO5)
  - Frequency counter (RPM calculation)

**Features:**
- Variable speed control (0-100%)
- RPM monitoring
- Stall detection
- Temperature-based speed curves
- Quiet mode (reduced minimum speed)

**Files:**
- `packages/expansions/fan_pwm.yaml`
- `packages/features/fan_control_profile.yaml`

#### 3.5.2 Fan Module - GP8403 Version
**Actuators:**
- **GP8403 DAC** (I2C, 0-10V or 0-5V analog output)
  - I2C Address: 0x58 or 0x59 (configurable)
  - Dual-channel 12-bit DAC
  - Voltage range: 0-10V or 0-5V (jumper selectable)
- **Use Case**: Control commercial HVAC fans, EC motors, variable frequency drives (VFDs)

**Features:**
- Precise voltage output (0.01V resolution)
- Two independent fan channels
- 0-10V industry-standard control
- Current monitoring (optional external ADC)

**Files:**
- `packages/expansions/fan_gp8403.yaml`
- `packages/features/fan_control_advanced_profile.yaml`

**Products Using This Module:**
- Sense360 Core + Fan (PWM)
- Sense360 Core + Fan (GP8403)
- Sense360 Bathroom + Fan

---

### 3.6 Sense360 Bathroom Module

**Purpose**: Bathroom-specific air quality and ventilation control

**Description**:
This is a specialized variant of the AirIQ module optimized for bathroom environments, with different sensors and thresholds.

**Sensors:**
- **SHT40**: Temperature and humidity (focus on humidity spikes)
  - I2C Address: 0x44
- **SCD41**: CO2 monitoring
  - I2C Address: 0x62
- **Optional VOC Sensor**: SGP40 or similar (detect odors)
  - I2C Address: 0x59
- **Optional Light Sensor**: BH1750 (detect room occupancy)
  - I2C Address: 0x23

**Features:**
- Shower detection (rapid humidity increase)
- Mold risk calculation (sustained high humidity)
- Automatic ventilation control
- Humidity-based fan speed curves
- Post-shower ventilation timer
- Odor detection and response

**Files:**
- `packages/expansions/bathroom.yaml` - Hardware driver
- `packages/features/bathroom_profile.yaml` - Bathroom-specific logic

**Products Using This Module:**
- Sense360 Core + Bathroom
- Sense360 Core + Bathroom + Fan (complete bathroom automation)

---

## 4. Configuration Architecture

### 4.1 Package Composition Pattern

**Example: Sense360 Core + AirIQ + Fan**

```yaml
# Product configuration file
packages:
  base: !include ../packages/base/complete.yaml
  core: !include ../packages/hardware/sense360_core.yaml
  power: !include ../packages/hardware/power_poe.yaml
  expansion_airiq: !include ../packages/expansions/airiq.yaml
  expansion_fan: !include ../packages/expansions/fan_pwm.yaml
  profile_airiq: !include ../packages/features/airiq_basic_profile.yaml
  profile_fan: !include ../packages/features/fan_control_profile.yaml

substitutions:
  device_name: sense360-core-airiq-fan
  friendly_name: "Sense360 AirIQ with Fan"

  # Power configuration
  power_source: "poe"  # or "240v", "usb"

  # I2C bus assignment
  airiq_i2c_bus: i2c0
  fan_i2c_bus: i2c0

  # Fan control
  fan_gpio: GPIO4
  fan_tach_gpio: GPIO5
```

### 4.2 Multi-Module Support

**Key Design Principles:**
1. **Unique IDs**: All sensors/entities must have unique IDs to avoid conflicts
2. **I2C Bus Sharing**: Multiple modules can share the same I2C bus (different addresses)
3. **UART Conflict Resolution**: Only one module per UART bus
4. **GPIO Allocation**: Expansion modules use designated GPIO pins

**Example: Core + AirIQ + Comfort + Presence + Fan**

```yaml
packages:
  base: !include ../packages/base/complete.yaml
  core: !include ../packages/hardware/sense360_core.yaml
  power: !include ../packages/hardware/power_240v.yaml

  # All expansion modules
  expansion_airiq: !include ../packages/expansions/airiq.yaml
  expansion_comfort: !include ../packages/expansions/comfort.yaml
  expansion_presence: !include ../packages/expansions/presence_ld2450.yaml
  expansion_fan: !include ../packages/expansions/fan_pwm.yaml

  # Feature profiles
  profile_airiq: !include ../packages/features/airiq_advanced_profile.yaml
  profile_comfort: !include ../packages/features/comfort_advanced_profile.yaml
  profile_presence: !include ../packages/features/presence_advanced_profile.yaml
  profile_fan: !include ../packages/features/fan_control_profile.yaml

substitutions:
  device_name: sense360-core-complete
  friendly_name: "Sense360 Ultimate"

  # I2C bus assignments (all modules share I2C)
  airiq_i2c_bus: i2c0
  comfort_i2c_bus: i2c0

  # UART assignment (presence sensor)
  presence_uart_bus: uart_bus

  # GPIO assignments
  fan_pwm_gpio: GPIO4
  fan_tach_gpio: GPIO5
```

---

## 5. Implementation Roadmap

### Phase 1: Core Board Foundation (Week 1-2)
**Deliverables:**
- [ ] Create `packages/hardware/sense360_core.yaml` (standard board definition)
- [ ] Create `packages/hardware/sense360_core_voice.yaml` (voice variant)
- [ ] Create power configuration packages:
  - [ ] `packages/hardware/power_240v.yaml`
  - [ ] `packages/hardware/power_poe.yaml`
  - [ ] `packages/hardware/power_usb.yaml`
- [ ] Document pin assignments and expansion bus specification
- [ ] Test basic connectivity (WiFi, API, OTA)

**Success Criteria:**
- Core board boots and connects to WiFi
- All power sources work correctly
- Expansion bus GPIOs and I2C functional

---

### Phase 2: Expansion Module Drivers (Week 3-4) ✅ COMPLETE
**Deliverables:**
- [x] Migrate existing hardware drivers to expansions:
  - [x] Move `packages/hardware/presence_ld2450.yaml` → `packages/expansions/presence_ld2450.yaml`
  - [x] Move `packages/hardware/presence_ld2412.yaml` → `packages/expansions/presence_ld2412.yaml`
- [x] Create new expansion drivers:
  - [x] `packages/expansions/airiq.yaml` (SEN55 + SCD41)
  - [x] `packages/expansions/comfort.yaml` (SHT40 + BH1750 + BME680)
  - [x] `packages/expansions/fan_pwm.yaml` (PWM control with tachometer)
  - [x] `packages/expansions/fan_gp8403.yaml` (Dual-channel DAC control)
  - [x] `packages/expansions/bathroom.yaml` (SHT40 + SCD41 + SGP40 + BH1750)
- [x] Ensure all drivers use `internal: true` for raw sensors
- [x] Create feature profiles (accelerated from Phase 3):
  - [x] `packages/features/comfort_basic_profile.yaml`
  - [x] `packages/features/comfort_advanced_profile.yaml`
  - [x] `packages/features/fan_control_profile.yaml`
  - [x] `packages/features/fan_control_advanced_profile.yaml`
  - [x] `packages/features/bathroom_profile.yaml`
- [ ] Test each expansion module independently

**Success Criteria:**
- All expansion modules detected on I2C scan
- Raw sensor data readable
- No conflicts between modules

**Completed**: 2025-12-04

---

### Phase 3: Feature Profiles (Week 5-6) - PARTIALLY COMPLETE
**Deliverables:**
- [x] Create/update feature profiles:
  - [x] `packages/features/airiq_basic_profile.yaml` (user-friendly) - existed
  - [x] `packages/features/airiq_advanced_profile.yaml` (technical) - existed
  - [x] `packages/features/comfort_basic_profile.yaml` - created in Phase 2
  - [x] `packages/features/comfort_advanced_profile.yaml` - created in Phase 2
  - [x] `packages/features/fan_control_profile.yaml` - created in Phase 2
  - [x] `packages/features/fan_control_advanced_profile.yaml` - created in Phase 2
  - [x] `packages/features/bathroom_profile.yaml` - created in Phase 2
- [x] Update existing presence profiles (already exist)
- [x] Implement template sensors for abstracted entities
- [x] Add automation logic (fan control based on humidity, etc.)

**Success Criteria:**
- User-facing entities are intuitive and well-named
- Advanced profiles expose all technical details
- Automations work correctly

---

### Phase 4: Product Configurations (Week 7-8)
**Deliverables:**
- [ ] Create product configuration files in `products/`:
  - [ ] `sense360-core-airiq.yaml`
  - [ ] `sense360-core-comfort.yaml`
  - [ ] `sense360-core-presence.yaml`
  - [ ] `sense360-core-fan-pwm.yaml`
  - [ ] `sense360-core-fan-gp8403.yaml`
  - [ ] `sense360-core-bathroom.yaml`
  - [ ] `sense360-core-voice-airiq.yaml`
  - [ ] `sense360-core-complete.yaml` (all modules)
- [ ] Create example configurations for users
- [ ] Test all product combinations
- [ ] Validate YAML syntax

**Success Criteria:**
- All product configs compile without errors
- Each product tested on physical hardware (if available)
- Documentation updated with product descriptions

---

### Phase 5: Documentation & Testing (Week 9-10)
**Deliverables:**
- [ ] Update `docs/configuration.md` with new products
- [ ] Create expansion module documentation:
  - [ ] `docs/EXPANSION_AIRIQ.md`
  - [ ] `docs/EXPANSION_COMFORT.md`
  - [ ] `docs/EXPANSION_PRESENCE.md`
  - [ ] `docs/EXPANSION_FAN.md`
  - [ ] `docs/EXPANSION_BATHROOM.md`
- [ ] Create hardware documentation:
  - [ ] `docs/CORE_BOARD.md` (pinout, specifications)
  - [ ] `docs/EXPANSION_BUS.md` (interface specification)
  - [ ] `docs/POWER_OPTIONS.md` (240V/PoE/USB setup)
- [ ] Add integration tests for expansion modules
- [ ] Create troubleshooting guide
- [ ] Add example automation recipes

**Success Criteria:**
- Complete documentation for all modules
- Users can self-serve configuration
- CI/CD validates all configs

---

### Phase 6: Voice Integration (Week 11-12, Optional)
**Deliverables:**
- [ ] Integrate ESPHome voice assistant component
- [ ] Configure I2S microphone (INMP441)
- [ ] Configure I2S speaker (MAX98357A)
- [ ] Implement wake word detection
- [ ] Create voice command handlers:
  - [ ] "What's the air quality?"
  - [ ] "What's the temperature?"
  - [ ] "Is anyone home?"
  - [ ] "Turn on the fan"
- [ ] Test voice latency and accuracy

**Success Criteria:**
- Voice commands work reliably (>90% accuracy)
- Response time < 2 seconds
- Works without cloud services

---

## 6. File Structure

```
esphome-public/
├── packages/
│   ├── base/                          # Core system packages (unchanged)
│   │   ├── complete.yaml
│   │   ├── wifi.yaml
│   │   ├── api_encrypted.yaml
│   │   ├── ota.yaml
│   │   ├── time.yaml
│   │   ├── logging.yaml
│   │   └── bluetooth_proxy.yaml
│   │
│   ├── hardware/                      # Core board definitions
│   │   ├── sense360_core.yaml         # NEW: Standard core board
│   │   ├── sense360_core_voice.yaml   # NEW: Voice-enabled core
│   │   ├── sense360_core_mini.yaml    # EXISTING: Mini board
│   │   ├── sense360_core_ceiling.yaml # EXISTING: Ceiling board
│   │   ├── power_240v.yaml            # NEW: AC power config
│   │   ├── power_poe.yaml             # NEW: PoE config
│   │   └── power_usb.yaml             # NEW: USB config
│   │
│   ├── expansions/                    # NEW: Expansion module drivers
│   │   ├── airiq.yaml                 # Air quality sensors
│   │   ├── comfort.yaml               # Environmental comfort sensors
│   │   ├── presence_ld2450.yaml       # mmWave presence (multi-target)
│   │   ├── presence_ld2412.yaml       # mmWave presence (single-zone)
│   │   ├── fan_pwm.yaml               # PWM fan control
│   │   ├── fan_gp8403.yaml            # DAC fan control (0-10V)
│   │   └── bathroom.yaml              # Bathroom-specific sensors
│   │
│   └── features/                      # Feature profiles (user-facing)
│       ├── airiq_basic_profile.yaml   # NEW: Basic air quality profile
│       ├── airiq_advanced_profile.yaml # NEW: Advanced air quality profile
│       ├── comfort_basic_profile.yaml # NEW: Basic comfort profile
│       ├── comfort_advanced_profile.yaml # NEW: Advanced comfort profile
│       ├── fan_control_profile.yaml   # NEW: Basic fan control
│       ├── fan_control_advanced_profile.yaml # NEW: Advanced fan control
│       ├── bathroom_profile.yaml      # NEW: Bathroom automation
│       ├── presence_basic_profile.yaml # EXISTING: Basic presence
│       ├── presence_advanced_profile.yaml # EXISTING: Advanced presence
│       ├── ceiling_halo_leds.yaml     # EXISTING: LED control
│       └── mini_four_leds_addr.yaml   # EXISTING: LED control
│
├── products/                          # Complete product configurations
│   ├── sense360-core-airiq.yaml       # NEW: Core + AirIQ
│   ├── sense360-core-comfort.yaml     # NEW: Core + Comfort
│   ├── sense360-core-presence.yaml    # NEW: Core + Presence
│   ├── sense360-core-fan-pwm.yaml     # NEW: Core + PWM Fan
│   ├── sense360-core-fan-gp8403.yaml  # NEW: Core + DAC Fan
│   ├── sense360-core-bathroom.yaml    # NEW: Core + Bathroom
│   ├── sense360-core-voice-airiq.yaml # NEW: Core Voice + AirIQ
│   ├── sense360-core-complete.yaml    # NEW: Core + All Modules
│   ├── sense360-mini-presence.yaml    # EXISTING
│   ├── sense360-mini-airiq.yaml       # EXISTING
│   └── sense360-ceiling-presence.yaml # EXISTING
│
├── docs/
│   ├── SENSE360_CORE_PLAN.md          # This document
│   ├── CORE_BOARD.md                  # NEW: Core board hardware docs
│   ├── EXPANSION_BUS.md               # NEW: Expansion interface spec
│   ├── POWER_OPTIONS.md               # NEW: Power configuration guide
│   ├── EXPANSION_AIRIQ.md             # NEW: AirIQ module docs
│   ├── EXPANSION_COMFORT.md           # NEW: Comfort module docs
│   ├── EXPANSION_PRESENCE.md          # NEW: Presence module docs
│   ├── EXPANSION_FAN.md               # NEW: Fan module docs
│   ├── EXPANSION_BATHROOM.md          # NEW: Bathroom module docs
│   ├── configuration.md               # EXISTING (update)
│   ├── installation.md                # EXISTING (update)
│   └── MVP_ROADMAP.md                 # EXISTING
│
└── examples/
    ├── sense360-core-airiq-example.yaml  # NEW: User template
    ├── sense360-core-bathroom-example.yaml # NEW: User template
    └── sense360-core-complete-example.yaml # NEW: User template
```

---

## 7. Key Design Decisions

### 7.1 Modular vs Monolithic
**Decision**: Fully modular architecture with expansion modules
**Rationale**:
- Maximum flexibility for users
- Lower cost for basic configurations
- Easy to add new modules without redesigning core board
- Enables third-party expansion modules

### 7.2 I2C Bus Sharing
**Decision**: Multiple expansion modules share the same I2C bus
**Rationale**:
- Simplifies connector design
- Standard I2C protocol supports multi-device
- Address conflicts are manageable (documented address ranges)
- Reduces pin count requirements

### 7.3 Power Source Priority
**Decision**: PoE > 240V AC > USB-C
**Rationale**:
- PoE provides most stable, isolated power
- 240V AC suitable for wall-mounted installations
- USB-C as fallback for development/testing

### 7.4 YAML Package Architecture
**Decision**: Maintain 3-layer package system (hardware/expansions/features)
**Rationale**:
- Separation of concerns (hardware vs user-facing)
- Reusable across multiple products
- Easy to maintain and test
- Consistent with existing architecture

### 7.5 Voice Integration
**Decision**: Separate core board variant (Core Voice) vs add-on module
**Rationale**:
- Voice requires significant power and PCB space
- I2S interface not easily sharable
- Not all users need voice functionality
- Keeps standard core board cost-effective

---

## 8. Hardware Specifications Summary

| Feature | Sense360 Core | Sense360 Core Voice |
|---------|---------------|---------------------|
| **MCU** | ESP32-S3 (8MB/2MB) | ESP32-S3 (8MB/2MB) |
| **WiFi** | 2.4GHz | 2.4GHz |
| **Bluetooth** | BLE 5.0 | BLE 5.0 |
| **Power Input** | 240V AC / PoE / USB-C | 240V AC / PoE (preferred) |
| **Power Output** | 5V/2A, 3.3V/1A | 5V/2A, 3.3V/1A |
| **I2C Buses** | 2x (primary + secondary) | 2x (primary + secondary) |
| **UART** | 1x (115200-256000 baud) | 1x (115200-256000 baud) |
| **GPIO Expansion** | 4x configurable | 4x configurable |
| **Relay** | 1x (10A, GPIO10) | 1x (10A, GPIO10) |
| **Status LEDs** | RGB + Status | RGB + Status |
| **Microphone** | - | I2S MEMS (INMP441) |
| **Speaker** | - | I2S DAC (MAX98357A, 3W) |
| **Dimensions** | TBD | TBD |
| **Weight** | TBD | TBD |

---

## 9. Expansion Module Compatibility Matrix

| Expansion Module | I2C Address | UART | GPIO | Power | Compatible Core Boards |
|------------------|-------------|------|------|-------|------------------------|
| **AirIQ** | 0x69, 0x62, 0x44 | - | - | 3.3V/500mA | All |
| **Comfort** | 0x44, 0x23, 0x76 | - | - | 3.3V/200mA | All |
| **Presence (LD2450)** | - | Yes | - | 5V/150mA | All |
| **Presence (LD2412)** | - | Yes | - | 5V/150mA | All |
| **Fan (PWM)** | - | - | GPIO4 | 5V/1A (external) | All |
| **Fan (GP8403)** | 0x58/0x59 | - | - | 3.3V/50mA | All |
| **Bathroom** | 0x44, 0x62, 0x59, 0x23 | - | - | 3.3V/500mA | All |

**Notes:**
- Multiple I2C modules can be used simultaneously (different addresses)
- Only one UART module at a time (use presence OR another UART device)
- Fan PWM uses GPIO, doesn't conflict with I2C modules
- Total power consumption must not exceed core board limits

---

## 10. Testing Strategy

### 10.1 Unit Tests
- [ ] Power management logic
- [ ] I2C device detection
- [ ] Sensor data parsing
- [ ] Template sensor calculations

### 10.2 Integration Tests
- [ ] Single expansion module with core board
- [ ] Multiple expansion modules simultaneously
- [ ] Power source switching (PoE → 240V → USB)
- [ ] OTA updates with all modules active

### 10.3 Hardware Tests
- [ ] Power consumption measurements
- [ ] I2C bus stability under load
- [ ] Temperature rise testing
- [ ] Electromagnetic compatibility (EMC)
- [ ] Safety testing (240V AC variant)

---

## 11. Open Questions & Future Work

### 11.1 Open Questions
1. **Physical connector type**: 10-pin header vs FPC vs custom connector?
2. **Module enclosures**: Individual enclosures or stackable design?
3. **Module auto-detection**: Should modules have EEPROM ID chips?
4. **Hot-swapping**: Support for module hot-plug/unplug?
5. **PoE standard**: IEEE 802.3af (15.4W) or 802.3at (30W) for high-power configs?

### 11.2 Future Expansion Ideas
- **Sense360 Display Module**: E-ink or OLED display for status
- **Sense360 Relay Module**: Multi-relay expansion (4x or 8x relays)
- **Sense360 LED Ring Module**: Addressable LED ring for visual feedback
- **Sense360 External Sensor Module**: Remote temperature/humidity probes
- **Sense360 Power Monitor Module**: AC power monitoring (CT clamps)

---

## 12. Success Metrics

| Metric | Target |
|--------|--------|
| **Core board boot time** | < 5 seconds |
| **Module auto-detection** | 100% success rate |
| **Power efficiency** | < 3W idle, < 8W full load |
| **I2C stability** | No bus errors over 24hr test |
| **Configuration compile time** | < 2 minutes per product |
| **User setup time** | < 15 minutes (plug & play) |
| **Documentation completeness** | 100% of modules documented |
| **Test coverage** | > 90% code coverage |

---

## 13. Next Steps

1. **Review & Approval**: Share this plan with stakeholders for feedback
2. **Hardware Prototyping**: Design and order PCBs for core board and expansions
3. **Software Foundation**: Create base YAML packages (Phase 1)
4. **Iterative Testing**: Test each module as hardware becomes available
5. **Documentation**: Write user-facing docs in parallel with development
6. **Beta Testing**: Deploy to early users for real-world validation

---

**Document Owner**: Development Team
**Last Updated**: 2025-12-04
**Next Review**: After Phase 1 completion
**Status**: Awaiting approval to proceed with implementation

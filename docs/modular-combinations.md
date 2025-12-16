# Sense360 Complete Modular Combinations List

This document provides an exhaustive list of all possible Sense360 product configurations.

---

## Quick Summary

| Category | Count |
|----------|-------|
| Base configurations (Core + Power only) | 12 |
| Ceiling module combinations | 69 |
| Wall module combinations | 45 |
| **Total unique configurations** | **126** |

> With presence sensor variants (LD2450, LD2412, C4001), the total expands to **200+ configurations**.

---

## System Components

### Core Boards (Pick 1)
| Core | SKU | Description |
|------|-----|-------------|
| Core | S360-CORE | Standard ESP32-S3 core |
| Core Voice | S360-CORE-V | Voice-enabled with mic support |

### Power Options (Pick 1)
| Power | SKU | Input | Use Case |
|-------|-----|-------|----------|
| USB | Built-in | 5V USB-C | Development, portable |
| PoE | S360-POE | 36-57V PoE | Professional install |
| PWR | S360-PWR | 100-240V AC | Permanent install |

### Form Factors (Pick 1)
| Mount | Suffix | Description |
|-------|--------|-------------|
| Ceiling | -C | Ceiling flush mount |
| Wall | -W | Wall or desk mount |

### Expansion Modules (Optional - Mix & Match)
| Module | SKU | Ceiling | Wall | Notes |
|--------|-----|---------|------|-------|
| AirIQ | S360-AIR | ✓ | ✓ | Full air quality suite |
| Bathroom Base | S360-BATH-B | ✓ | ✗ | Replaces AirIQ |
| Bathroom Pro | S360-BATH-P | ✓ | ✗ | Replaces AirIQ |
| Comfort | S360-CMFT | ✓ | ✓ | Temp/humidity/light |
| Presence | S360-PRES | ✓ | ✓ | mmWave radar |
| Fan PWM | S360-PWM | ✓ | ✓ | PWM fan control |
| Fan GP8403 | S360-GP8403 | ✓ | ✓ | 0-10V DAC fan control |

### Presence Sensor Variants
| Sensor | Features | Best For |
|--------|----------|----------|
| HLK-LD2450 | Multi-target (3), distance/angle | Default, general use |
| HLK-LD2412 | Single-zone, better still detection | Bedrooms, offices |
| DFRobot C4001 | Long-range (16m/25m), speed | Large spaces |

---

## Constraints

1. **AirIQ ⚔️ Bathroom** - Mutually exclusive (cannot use both)
2. **Bathroom → Ceiling only** - Not available for wall mount
3. **Fan PWM ⚔️ Fan GP8403** - Pick one fan control method
4. **Core Voice → LED+MIC required** - Must include voice-enabled LED ring

---

## Part 1: Base Configurations (No Expansion Modules)

These are Core + Power only configurations with no sensor modules.

### Standard Core Base (6 configurations)

| # | Configuration | SKU Pattern |
|---|---------------|-------------|
| 1 | Core + Ceiling + USB | S360-CORE-C-USB |
| 2 | Core + Ceiling + PoE | S360-CORE-C-POE |
| 3 | Core + Ceiling + PWR | S360-CORE-C-PWR |
| 4 | Core + Wall + USB | S360-CORE-W-USB |
| 5 | Core + Wall + PoE | S360-CORE-W-POE |
| 6 | Core + Wall + PWR | S360-CORE-W-PWR |

### Voice Core Base (6 configurations)

| # | Configuration | SKU Pattern |
|---|---------------|-------------|
| 7 | Core Voice + Ceiling + USB | S360-CORE-V-C-USB |
| 8 | Core Voice + Ceiling + PoE | S360-CORE-V-C-POE |
| 9 | Core Voice + Ceiling + PWR | S360-CORE-V-C-PWR |
| 10 | Core Voice + Wall + USB | S360-CORE-V-W-USB |
| 11 | Core Voice + Wall + PoE | S360-CORE-V-W-POE |
| 12 | Core Voice + Wall + PWR | S360-CORE-V-W-PWR |

**Base Total: 12 configurations**

---

## Part 2: Ceiling Mount Configurations

All combinations for ceiling-mounted cores (Core-C or Core-V-C).

### Single Module (Ceiling)

| # | Modules | × Power Options | = Configs |
|---|---------|-----------------|-----------|
| 1 | AirIQ | × 3 | 3 |
| 2 | Bathroom Base | × 3 | 3 |
| 3 | Bathroom Pro | × 3 | 3 |
| 4 | Comfort | × 3 | 3 |
| 5 | Presence | × 3 | 3 |
| 6 | Fan PWM | × 3 | 3 |
| 7 | Fan GP8403 | × 3 | 3 |
| | **Subtotal** | | **21** |

#### Detailed Single Module List (Ceiling)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-C + AirIQ | ✓ | ✓ | ✓ |
| 2 | Core-C + Bathroom Base | ✓ | ✓ | ✓ |
| 3 | Core-C + Bathroom Pro | ✓ | ✓ | ✓ |
| 4 | Core-C + Comfort | ✓ | ✓ | ✓ |
| 5 | Core-C + Presence | ✓ | ✓ | ✓ |
| 6 | Core-C + Fan PWM | ✓ | ✓ | ✓ |
| 7 | Core-C + Fan GP8403 | ✓ | ✓ | ✓ |

---

### Two Module Combinations (Ceiling)

| # | Modules | × Power | = Configs |
|---|---------|---------|-----------|
| 1 | AirIQ + Comfort | × 3 | 3 |
| 2 | AirIQ + Presence | × 3 | 3 |
| 3 | AirIQ + Fan PWM | × 3 | 3 |
| 4 | AirIQ + Fan GP8403 | × 3 | 3 |
| 5 | Bathroom Base + Comfort | × 3 | 3 |
| 6 | Bathroom Base + Presence | × 3 | 3 |
| 7 | Bathroom Base + Fan PWM | × 3 | 3 |
| 8 | Bathroom Base + Fan GP8403 | × 3 | 3 |
| 9 | Bathroom Pro + Comfort | × 3 | 3 |
| 10 | Bathroom Pro + Presence | × 3 | 3 |
| 11 | Bathroom Pro + Fan PWM | × 3 | 3 |
| 12 | Bathroom Pro + Fan GP8403 | × 3 | 3 |
| 13 | Comfort + Presence | × 3 | 3 |
| 14 | Comfort + Fan PWM | × 3 | 3 |
| 15 | Comfort + Fan GP8403 | × 3 | 3 |
| 16 | Presence + Fan PWM | × 3 | 3 |
| 17 | Presence + Fan GP8403 | × 3 | 3 |
| | **Subtotal** | | **51** |

#### Detailed Two Module List (Ceiling)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-C + AirIQ + Comfort | ✓ | ✓ | ✓ |
| 2 | Core-C + AirIQ + Presence | ✓ | ✓ | ✓ |
| 3 | Core-C + AirIQ + Fan PWM | ✓ | ✓ | ✓ |
| 4 | Core-C + AirIQ + Fan GP8403 | ✓ | ✓ | ✓ |
| 5 | Core-C + Bathroom Base + Comfort | ✓ | ✓ | ✓ |
| 6 | Core-C + Bathroom Base + Presence | ✓ | ✓ | ✓ |
| 7 | Core-C + Bathroom Base + Fan PWM | ✓ | ✓ | ✓ |
| 8 | Core-C + Bathroom Base + Fan GP8403 | ✓ | ✓ | ✓ |
| 9 | Core-C + Bathroom Pro + Comfort | ✓ | ✓ | ✓ |
| 10 | Core-C + Bathroom Pro + Presence | ✓ | ✓ | ✓ |
| 11 | Core-C + Bathroom Pro + Fan PWM | ✓ | ✓ | ✓ |
| 12 | Core-C + Bathroom Pro + Fan GP8403 | ✓ | ✓ | ✓ |
| 13 | Core-C + Comfort + Presence | ✓ | ✓ | ✓ |
| 14 | Core-C + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 15 | Core-C + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 16 | Core-C + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 17 | Core-C + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

---

### Three Module Combinations (Ceiling)

| # | Modules | × Power | = Configs |
|---|---------|---------|-----------|
| 1 | AirIQ + Comfort + Presence | × 3 | 3 |
| 2 | AirIQ + Comfort + Fan PWM | × 3 | 3 |
| 3 | AirIQ + Comfort + Fan GP8403 | × 3 | 3 |
| 4 | AirIQ + Presence + Fan PWM | × 3 | 3 |
| 5 | AirIQ + Presence + Fan GP8403 | × 3 | 3 |
| 6 | Bathroom Base + Comfort + Presence | × 3 | 3 |
| 7 | Bathroom Base + Comfort + Fan PWM | × 3 | 3 |
| 8 | Bathroom Base + Comfort + Fan GP8403 | × 3 | 3 |
| 9 | Bathroom Base + Presence + Fan PWM | × 3 | 3 |
| 10 | Bathroom Base + Presence + Fan GP8403 | × 3 | 3 |
| 11 | Bathroom Pro + Comfort + Presence | × 3 | 3 |
| 12 | Bathroom Pro + Comfort + Fan PWM | × 3 | 3 |
| 13 | Bathroom Pro + Comfort + Fan GP8403 | × 3 | 3 |
| 14 | Bathroom Pro + Presence + Fan PWM | × 3 | 3 |
| 15 | Bathroom Pro + Presence + Fan GP8403 | × 3 | 3 |
| 16 | Comfort + Presence + Fan PWM | × 3 | 3 |
| 17 | Comfort + Presence + Fan GP8403 | × 3 | 3 |
| | **Subtotal** | | **51** |

#### Detailed Three Module List (Ceiling)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-C + AirIQ + Comfort + Presence | ✓ | ✓ | ✓ |
| 2 | Core-C + AirIQ + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 3 | Core-C + AirIQ + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 4 | Core-C + AirIQ + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 5 | Core-C + AirIQ + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 6 | Core-C + Bathroom Base + Comfort + Presence | ✓ | ✓ | ✓ |
| 7 | Core-C + Bathroom Base + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 8 | Core-C + Bathroom Base + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 9 | Core-C + Bathroom Base + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 10 | Core-C + Bathroom Base + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 11 | Core-C + Bathroom Pro + Comfort + Presence | ✓ | ✓ | ✓ |
| 12 | Core-C + Bathroom Pro + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 13 | Core-C + Bathroom Pro + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 14 | Core-C + Bathroom Pro + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 15 | Core-C + Bathroom Pro + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 16 | Core-C + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 17 | Core-C + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

---

### Four Module Combinations (Ceiling)

| # | Modules | × Power | = Configs |
|---|---------|---------|-----------|
| 1 | AirIQ + Comfort + Presence + Fan PWM | × 3 | 3 |
| 2 | AirIQ + Comfort + Presence + Fan GP8403 | × 3 | 3 |
| 3 | Bathroom Base + Comfort + Presence + Fan PWM | × 3 | 3 |
| 4 | Bathroom Base + Comfort + Presence + Fan GP8403 | × 3 | 3 |
| 5 | Bathroom Pro + Comfort + Presence + Fan PWM | × 3 | 3 |
| 6 | Bathroom Pro + Comfort + Presence + Fan GP8403 | × 3 | 3 |
| | **Subtotal** | | **18** |

#### Detailed Four Module List (Ceiling)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-C + AirIQ + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 2 | Core-C + AirIQ + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 3 | Core-C + Bathroom Base + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 4 | Core-C + Bathroom Base + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 5 | Core-C + Bathroom Pro + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 6 | Core-C + Bathroom Pro + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

---

### Ceiling Mount Summary

| Category | Module Combos | × Power | = Total |
|----------|---------------|---------|---------|
| Single Module | 7 | × 3 | 21 |
| Two Modules | 17 | × 3 | 51 |
| Three Modules | 17 | × 3 | 51 |
| Four Modules | 6 | × 3 | 18 |
| **Ceiling Total** | **47** | | **141** |

> Double for Voice variants (Core-V-C): **282 ceiling configurations**

---

## Part 3: Wall Mount Configurations

All combinations for wall-mounted cores (Core-W or Core-V-W).

> **Note:** No Bathroom modules available for Wall mount.

### Single Module (Wall)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-W + AirIQ | ✓ | ✓ | ✓ |
| 2 | Core-W + Comfort | ✓ | ✓ | ✓ |
| 3 | Core-W + Presence | ✓ | ✓ | ✓ |
| 4 | Core-W + Fan PWM | ✓ | ✓ | ✓ |
| 5 | Core-W + Fan GP8403 | ✓ | ✓ | ✓ |

**Subtotal: 5 × 3 = 15 configurations**

---

### Two Module Combinations (Wall)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-W + AirIQ + Comfort | ✓ | ✓ | ✓ |
| 2 | Core-W + AirIQ + Presence | ✓ | ✓ | ✓ |
| 3 | Core-W + AirIQ + Fan PWM | ✓ | ✓ | ✓ |
| 4 | Core-W + AirIQ + Fan GP8403 | ✓ | ✓ | ✓ |
| 5 | Core-W + Comfort + Presence | ✓ | ✓ | ✓ |
| 6 | Core-W + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 7 | Core-W + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 8 | Core-W + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 9 | Core-W + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

**Subtotal: 9 × 3 = 27 configurations**

---

### Three Module Combinations (Wall)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-W + AirIQ + Comfort + Presence | ✓ | ✓ | ✓ |
| 2 | Core-W + AirIQ + Comfort + Fan PWM | ✓ | ✓ | ✓ |
| 3 | Core-W + AirIQ + Comfort + Fan GP8403 | ✓ | ✓ | ✓ |
| 4 | Core-W + AirIQ + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 5 | Core-W + AirIQ + Presence + Fan GP8403 | ✓ | ✓ | ✓ |
| 6 | Core-W + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 7 | Core-W + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

**Subtotal: 7 × 3 = 21 configurations**

---

### Four Module Combinations (Wall)

| # | Configuration | USB | PoE | PWR |
|---|---------------|-----|-----|-----|
| 1 | Core-W + AirIQ + Comfort + Presence + Fan PWM | ✓ | ✓ | ✓ |
| 2 | Core-W + AirIQ + Comfort + Presence + Fan GP8403 | ✓ | ✓ | ✓ |

**Subtotal: 2 × 3 = 6 configurations**

---

### Wall Mount Summary

| Category | Module Combos | × Power | = Total |
|----------|---------------|---------|---------|
| Single Module | 5 | × 3 | 15 |
| Two Modules | 9 | × 3 | 27 |
| Three Modules | 7 | × 3 | 21 |
| Four Modules | 2 | × 3 | 6 |
| **Wall Total** | **23** | | **69** |

> Double for Voice variants (Core-V-W): **138 wall configurations**

---

## Part 4: Complete Enumerated List

### All Ceiling Configurations (Standard Core)

| # | Core | Power | Air Quality | Comfort | Presence | Fan |
|---|------|-------|-------------|---------|----------|-----|
| 1 | Core-C | USB | - | - | - | - |
| 2 | Core-C | PoE | - | - | - | - |
| 3 | Core-C | PWR | - | - | - | - |
| 4 | Core-C | USB | AirIQ | - | - | - |
| 5 | Core-C | PoE | AirIQ | - | - | - |
| 6 | Core-C | PWR | AirIQ | - | - | - |
| 7 | Core-C | USB | Bathroom Base | - | - | - |
| 8 | Core-C | PoE | Bathroom Base | - | - | - |
| 9 | Core-C | PWR | Bathroom Base | - | - | - |
| 10 | Core-C | USB | Bathroom Pro | - | - | - |
| 11 | Core-C | PoE | Bathroom Pro | - | - | - |
| 12 | Core-C | PWR | Bathroom Pro | - | - | - |
| 13 | Core-C | USB | - | Comfort | - | - |
| 14 | Core-C | PoE | - | Comfort | - | - |
| 15 | Core-C | PWR | - | Comfort | - | - |
| 16 | Core-C | USB | - | - | Presence | - |
| 17 | Core-C | PoE | - | - | Presence | - |
| 18 | Core-C | PWR | - | - | Presence | - |
| 19 | Core-C | USB | - | - | - | PWM |
| 20 | Core-C | PoE | - | - | - | PWM |
| 21 | Core-C | PWR | - | - | - | PWM |
| 22 | Core-C | USB | - | - | - | GP8403 |
| 23 | Core-C | PoE | - | - | - | GP8403 |
| 24 | Core-C | PWR | - | - | - | GP8403 |
| 25 | Core-C | USB | AirIQ | Comfort | - | - |
| 26 | Core-C | PoE | AirIQ | Comfort | - | - |
| 27 | Core-C | PWR | AirIQ | Comfort | - | - |
| 28 | Core-C | USB | AirIQ | - | Presence | - |
| 29 | Core-C | PoE | AirIQ | - | Presence | - |
| 30 | Core-C | PWR | AirIQ | - | Presence | - |
| 31 | Core-C | USB | AirIQ | - | - | PWM |
| 32 | Core-C | PoE | AirIQ | - | - | PWM |
| 33 | Core-C | PWR | AirIQ | - | - | PWM |
| 34 | Core-C | USB | AirIQ | - | - | GP8403 |
| 35 | Core-C | PoE | AirIQ | - | - | GP8403 |
| 36 | Core-C | PWR | AirIQ | - | - | GP8403 |
| 37 | Core-C | USB | Bathroom Base | Comfort | - | - |
| 38 | Core-C | PoE | Bathroom Base | Comfort | - | - |
| 39 | Core-C | PWR | Bathroom Base | Comfort | - | - |
| 40 | Core-C | USB | Bathroom Base | - | Presence | - |
| 41 | Core-C | PoE | Bathroom Base | - | Presence | - |
| 42 | Core-C | PWR | Bathroom Base | - | Presence | - |
| 43 | Core-C | USB | Bathroom Base | - | - | PWM |
| 44 | Core-C | PoE | Bathroom Base | - | - | PWM |
| 45 | Core-C | PWR | Bathroom Base | - | - | PWM |
| 46 | Core-C | USB | Bathroom Base | - | - | GP8403 |
| 47 | Core-C | PoE | Bathroom Base | - | - | GP8403 |
| 48 | Core-C | PWR | Bathroom Base | - | - | GP8403 |
| 49 | Core-C | USB | Bathroom Pro | Comfort | - | - |
| 50 | Core-C | PoE | Bathroom Pro | Comfort | - | - |
| 51 | Core-C | PWR | Bathroom Pro | Comfort | - | - |
| 52 | Core-C | USB | Bathroom Pro | - | Presence | - |
| 53 | Core-C | PoE | Bathroom Pro | - | Presence | - |
| 54 | Core-C | PWR | Bathroom Pro | - | Presence | - |
| 55 | Core-C | USB | Bathroom Pro | - | - | PWM |
| 56 | Core-C | PoE | Bathroom Pro | - | - | PWM |
| 57 | Core-C | PWR | Bathroom Pro | - | - | PWM |
| 58 | Core-C | USB | Bathroom Pro | - | - | GP8403 |
| 59 | Core-C | PoE | Bathroom Pro | - | - | GP8403 |
| 60 | Core-C | PWR | Bathroom Pro | - | - | GP8403 |
| 61 | Core-C | USB | - | Comfort | Presence | - |
| 62 | Core-C | PoE | - | Comfort | Presence | - |
| 63 | Core-C | PWR | - | Comfort | Presence | - |
| 64 | Core-C | USB | - | Comfort | - | PWM |
| 65 | Core-C | PoE | - | Comfort | - | PWM |
| 66 | Core-C | PWR | - | Comfort | - | PWM |
| 67 | Core-C | USB | - | Comfort | - | GP8403 |
| 68 | Core-C | PoE | - | Comfort | - | GP8403 |
| 69 | Core-C | PWR | - | Comfort | - | GP8403 |
| 70 | Core-C | USB | - | - | Presence | PWM |
| 71 | Core-C | PoE | - | - | Presence | PWM |
| 72 | Core-C | PWR | - | - | Presence | PWM |
| 73 | Core-C | USB | - | - | Presence | GP8403 |
| 74 | Core-C | PoE | - | - | Presence | GP8403 |
| 75 | Core-C | PWR | - | - | Presence | GP8403 |
| 76 | Core-C | USB | AirIQ | Comfort | Presence | - |
| 77 | Core-C | PoE | AirIQ | Comfort | Presence | - |
| 78 | Core-C | PWR | AirIQ | Comfort | Presence | - |
| 79 | Core-C | USB | AirIQ | Comfort | - | PWM |
| 80 | Core-C | PoE | AirIQ | Comfort | - | PWM |
| 81 | Core-C | PWR | AirIQ | Comfort | - | PWM |
| 82 | Core-C | USB | AirIQ | Comfort | - | GP8403 |
| 83 | Core-C | PoE | AirIQ | Comfort | - | GP8403 |
| 84 | Core-C | PWR | AirIQ | Comfort | - | GP8403 |
| 85 | Core-C | USB | AirIQ | - | Presence | PWM |
| 86 | Core-C | PoE | AirIQ | - | Presence | PWM |
| 87 | Core-C | PWR | AirIQ | - | Presence | PWM |
| 88 | Core-C | USB | AirIQ | - | Presence | GP8403 |
| 89 | Core-C | PoE | AirIQ | - | Presence | GP8403 |
| 90 | Core-C | PWR | AirIQ | - | Presence | GP8403 |
| 91 | Core-C | USB | Bathroom Base | Comfort | Presence | - |
| 92 | Core-C | PoE | Bathroom Base | Comfort | Presence | - |
| 93 | Core-C | PWR | Bathroom Base | Comfort | Presence | - |
| 94 | Core-C | USB | Bathroom Base | Comfort | - | PWM |
| 95 | Core-C | PoE | Bathroom Base | Comfort | - | PWM |
| 96 | Core-C | PWR | Bathroom Base | Comfort | - | PWM |
| 97 | Core-C | USB | Bathroom Base | Comfort | - | GP8403 |
| 98 | Core-C | PoE | Bathroom Base | Comfort | - | GP8403 |
| 99 | Core-C | PWR | Bathroom Base | Comfort | - | GP8403 |
| 100 | Core-C | USB | Bathroom Base | - | Presence | PWM |
| 101 | Core-C | PoE | Bathroom Base | - | Presence | PWM |
| 102 | Core-C | PWR | Bathroom Base | - | Presence | PWM |
| 103 | Core-C | USB | Bathroom Base | - | Presence | GP8403 |
| 104 | Core-C | PoE | Bathroom Base | - | Presence | GP8403 |
| 105 | Core-C | PWR | Bathroom Base | - | Presence | GP8403 |
| 106 | Core-C | USB | Bathroom Pro | Comfort | Presence | - |
| 107 | Core-C | PoE | Bathroom Pro | Comfort | Presence | - |
| 108 | Core-C | PWR | Bathroom Pro | Comfort | Presence | - |
| 109 | Core-C | USB | Bathroom Pro | Comfort | - | PWM |
| 110 | Core-C | PoE | Bathroom Pro | Comfort | - | PWM |
| 111 | Core-C | PWR | Bathroom Pro | Comfort | - | PWM |
| 112 | Core-C | USB | Bathroom Pro | Comfort | - | GP8403 |
| 113 | Core-C | PoE | Bathroom Pro | Comfort | - | GP8403 |
| 114 | Core-C | PWR | Bathroom Pro | Comfort | - | GP8403 |
| 115 | Core-C | USB | Bathroom Pro | - | Presence | PWM |
| 116 | Core-C | PoE | Bathroom Pro | - | Presence | PWM |
| 117 | Core-C | PWR | Bathroom Pro | - | Presence | PWM |
| 118 | Core-C | USB | Bathroom Pro | - | Presence | GP8403 |
| 119 | Core-C | PoE | Bathroom Pro | - | Presence | GP8403 |
| 120 | Core-C | PWR | Bathroom Pro | - | Presence | GP8403 |
| 121 | Core-C | USB | - | Comfort | Presence | PWM |
| 122 | Core-C | PoE | - | Comfort | Presence | PWM |
| 123 | Core-C | PWR | - | Comfort | Presence | PWM |
| 124 | Core-C | USB | - | Comfort | Presence | GP8403 |
| 125 | Core-C | PoE | - | Comfort | Presence | GP8403 |
| 126 | Core-C | PWR | - | Comfort | Presence | GP8403 |
| 127 | Core-C | USB | AirIQ | Comfort | Presence | PWM |
| 128 | Core-C | PoE | AirIQ | Comfort | Presence | PWM |
| 129 | Core-C | PWR | AirIQ | Comfort | Presence | PWM |
| 130 | Core-C | USB | AirIQ | Comfort | Presence | GP8403 |
| 131 | Core-C | PoE | AirIQ | Comfort | Presence | GP8403 |
| 132 | Core-C | PWR | AirIQ | Comfort | Presence | GP8403 |
| 133 | Core-C | USB | Bathroom Base | Comfort | Presence | PWM |
| 134 | Core-C | PoE | Bathroom Base | Comfort | Presence | PWM |
| 135 | Core-C | PWR | Bathroom Base | Comfort | Presence | PWM |
| 136 | Core-C | USB | Bathroom Base | Comfort | Presence | GP8403 |
| 137 | Core-C | PoE | Bathroom Base | Comfort | Presence | GP8403 |
| 138 | Core-C | PWR | Bathroom Base | Comfort | Presence | GP8403 |
| 139 | Core-C | USB | Bathroom Pro | Comfort | Presence | PWM |
| 140 | Core-C | PoE | Bathroom Pro | Comfort | Presence | PWM |
| 141 | Core-C | PWR | Bathroom Pro | Comfort | Presence | PWM |
| 142 | Core-C | USB | Bathroom Pro | Comfort | Presence | GP8403 |
| 143 | Core-C | PoE | Bathroom Pro | Comfort | Presence | GP8403 |
| 144 | Core-C | PWR | Bathroom Pro | Comfort | Presence | GP8403 |

**Ceiling Standard Core Total: 144 configurations**

---

### All Wall Configurations (Standard Core)

| # | Core | Power | Air Quality | Comfort | Presence | Fan |
|---|------|-------|-------------|---------|----------|-----|
| 1 | Core-W | USB | - | - | - | - |
| 2 | Core-W | PoE | - | - | - | - |
| 3 | Core-W | PWR | - | - | - | - |
| 4 | Core-W | USB | AirIQ | - | - | - |
| 5 | Core-W | PoE | AirIQ | - | - | - |
| 6 | Core-W | PWR | AirIQ | - | - | - |
| 7 | Core-W | USB | - | Comfort | - | - |
| 8 | Core-W | PoE | - | Comfort | - | - |
| 9 | Core-W | PWR | - | Comfort | - | - |
| 10 | Core-W | USB | - | - | Presence | - |
| 11 | Core-W | PoE | - | - | Presence | - |
| 12 | Core-W | PWR | - | - | Presence | - |
| 13 | Core-W | USB | - | - | - | PWM |
| 14 | Core-W | PoE | - | - | - | PWM |
| 15 | Core-W | PWR | - | - | - | PWM |
| 16 | Core-W | USB | - | - | - | GP8403 |
| 17 | Core-W | PoE | - | - | - | GP8403 |
| 18 | Core-W | PWR | - | - | - | GP8403 |
| 19 | Core-W | USB | AirIQ | Comfort | - | - |
| 20 | Core-W | PoE | AirIQ | Comfort | - | - |
| 21 | Core-W | PWR | AirIQ | Comfort | - | - |
| 22 | Core-W | USB | AirIQ | - | Presence | - |
| 23 | Core-W | PoE | AirIQ | - | Presence | - |
| 24 | Core-W | PWR | AirIQ | - | Presence | - |
| 25 | Core-W | USB | AirIQ | - | - | PWM |
| 26 | Core-W | PoE | AirIQ | - | - | PWM |
| 27 | Core-W | PWR | AirIQ | - | - | PWM |
| 28 | Core-W | USB | AirIQ | - | - | GP8403 |
| 29 | Core-W | PoE | AirIQ | - | - | GP8403 |
| 30 | Core-W | PWR | AirIQ | - | - | GP8403 |
| 31 | Core-W | USB | - | Comfort | Presence | - |
| 32 | Core-W | PoE | - | Comfort | Presence | - |
| 33 | Core-W | PWR | - | Comfort | Presence | - |
| 34 | Core-W | USB | - | Comfort | - | PWM |
| 35 | Core-W | PoE | - | Comfort | - | PWM |
| 36 | Core-W | PWR | - | Comfort | - | PWM |
| 37 | Core-W | USB | - | Comfort | - | GP8403 |
| 38 | Core-W | PoE | - | Comfort | - | GP8403 |
| 39 | Core-W | PWR | - | Comfort | - | GP8403 |
| 40 | Core-W | USB | - | - | Presence | PWM |
| 41 | Core-W | PoE | - | - | Presence | PWM |
| 42 | Core-W | PWR | - | - | Presence | PWM |
| 43 | Core-W | USB | - | - | Presence | GP8403 |
| 44 | Core-W | PoE | - | - | Presence | GP8403 |
| 45 | Core-W | PWR | - | - | Presence | GP8403 |
| 46 | Core-W | USB | AirIQ | Comfort | Presence | - |
| 47 | Core-W | PoE | AirIQ | Comfort | Presence | - |
| 48 | Core-W | PWR | AirIQ | Comfort | Presence | - |
| 49 | Core-W | USB | AirIQ | Comfort | - | PWM |
| 50 | Core-W | PoE | AirIQ | Comfort | - | PWM |
| 51 | Core-W | PWR | AirIQ | Comfort | - | PWM |
| 52 | Core-W | USB | AirIQ | Comfort | - | GP8403 |
| 53 | Core-W | PoE | AirIQ | Comfort | - | GP8403 |
| 54 | Core-W | PWR | AirIQ | Comfort | - | GP8403 |
| 55 | Core-W | USB | AirIQ | - | Presence | PWM |
| 56 | Core-W | PoE | AirIQ | - | Presence | PWM |
| 57 | Core-W | PWR | AirIQ | - | Presence | PWM |
| 58 | Core-W | USB | AirIQ | - | Presence | GP8403 |
| 59 | Core-W | PoE | AirIQ | - | Presence | GP8403 |
| 60 | Core-W | PWR | AirIQ | - | Presence | GP8403 |
| 61 | Core-W | USB | - | Comfort | Presence | PWM |
| 62 | Core-W | PoE | - | Comfort | Presence | PWM |
| 63 | Core-W | PWR | - | Comfort | Presence | PWM |
| 64 | Core-W | USB | - | Comfort | Presence | GP8403 |
| 65 | Core-W | PoE | - | Comfort | Presence | GP8403 |
| 66 | Core-W | PWR | - | Comfort | Presence | GP8403 |
| 67 | Core-W | USB | AirIQ | Comfort | Presence | PWM |
| 68 | Core-W | PoE | AirIQ | Comfort | Presence | PWM |
| 69 | Core-W | PWR | AirIQ | Comfort | Presence | PWM |
| 70 | Core-W | USB | AirIQ | Comfort | Presence | GP8403 |
| 71 | Core-W | PoE | AirIQ | Comfort | Presence | GP8403 |
| 72 | Core-W | PWR | AirIQ | Comfort | Presence | GP8403 |

**Wall Standard Core Total: 72 configurations**

---

## Grand Total Summary

| Category | Standard Core | Voice Core | Total |
|----------|---------------|------------|-------|
| Ceiling configurations | 144 | 144 | 288 |
| Wall configurations | 72 | 72 | 144 |
| **Grand Total** | **216** | **216** | **432** |

### With Presence Sensor Variants

Each configuration with Presence can use one of 3 sensor variants:
- HLK-LD2450 (default)
- HLK-LD2412
- DFRobot C4001

This multiplies presence-enabled configurations by 3, resulting in **700+ unique configurations**.

---

## Appendix: Module Variants Reference

### Air Quality Module Variants

| Variant | SKU | Sensors | Use Case |
|---------|-----|---------|----------|
| AirIQ | S360-AIR | SPS30, SGP41, SCD41, BMP390 | General air quality |
| Bathroom Base | S360-BATH-B | SHT4x, BMP390, SGP41 | Basic bathroom |
| Bathroom Pro | S360-BATH-P | SHT4x, BMP390, SGP41, MLX90614, SPS30 | Full bathroom |

### Fan Control Variants

| Variant | SKU | Interface | Use Case |
|---------|-----|-----------|----------|
| Fan PWM | S360-PWM | 25kHz PWM | PC fans, standard PWM |
| Fan GP8403 | S360-GP8403 | 0-10V DAC | Commercial HVAC, VFDs |
| Relay | Built-in | On/Off | Simple switching |

### Presence Sensor Variants

| Variant | Features | Range | Use Case |
|---------|----------|-------|----------|
| HLK-LD2450 | Multi-target (3), distance/angle | 6m | Default, multi-person |
| HLK-LD2412 | Single-zone, still detection | 5m | Bedrooms, offices |
| DFRobot C4001 | Long-range, speed detection | 16m/25m | Large spaces |

---

## Package File Reference

### Core + Power Packages

```yaml
# Ceiling Core
packages/hardware/sense360_core_ceiling.yaml

# Wall Core
packages/hardware/sense360_core_wall.yaml

# Voice Ceiling Core
packages/hardware/sense360_core_voice_ceiling.yaml

# Voice Wall Core
packages/hardware/sense360_core_voice_wall.yaml

# Power - PoE
packages/hardware/power_poe.yaml

# Power - 240V AC
packages/hardware/power_240v.yaml

# Power - USB (built into core, no separate package)
```

### Expansion Module Packages

```yaml
# AirIQ
packages/expansions/airiq_ceiling.yaml
packages/expansions/airiq_wall.yaml

# Bathroom
packages/expansions/airiq_bathroom_base.yaml
packages/expansions/airiq_bathroom_pro.yaml

# Comfort
packages/expansions/comfort_ceiling.yaml
packages/expansions/comfort_wall.yaml

# Presence
packages/expansions/presence_ceiling.yaml
packages/expansions/presence_wall.yaml

# Fan Control
packages/expansions/fan_pwm.yaml
packages/expansions/fan_gp8403.yaml
```

### Presence Sensor Variant Packages

```yaml
# LD2450 (default - included in presence_*.yaml)
packages/hardware/presence_ld2450.yaml

# LD2412 (alternative)
packages/hardware/presence_ld2412.yaml

# DFRobot C4001 (long-range alternative)
packages/hardware/presence_dfrobot_c4001.yaml
```

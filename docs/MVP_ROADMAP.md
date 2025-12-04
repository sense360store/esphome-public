# Sense360 MVP Feature Roadmap

**Created**: 2025-12-04
**Version**: 2.2.0 Planning
**Status**: Active Development

---

## Executive Summary

This document prioritizes all remaining MVP features for Sense360 ESPHome firmware. Work is organized into 4 priority tiers based on impact, dependencies, and complexity.

**Current State**: v2.1.0 released with Phase 1 testing complete (133 unit tests)

---

## Priority Matrix

| Priority | Focus Area | Estimated Effort | Dependencies |
|----------|------------|------------------|--------------|
| **P1** | Testing Infrastructure | 4-5 weeks | None |
| **P2** | Core Product Features | 3-4 weeks | P1 partial |
| **P3** | Enhancement Features | 4-6 weeks | P2 |
| **P4** | Long-term Infrastructure | Ongoing | P1-P3 |

---

## P1: Testing Infrastructure (Critical Foundation)

These items ensure code quality and prevent regressions. **Must complete before major feature work.**

### 1.1 Phase 2: Integration Testing with Hardware Mocks
**Effort**: 3-4 weeks
**Status**: Not Started

**Deliverables:**
- [ ] Mock sensor framework for SEN55 (PM, VOC, NOx)
- [ ] Mock sensor framework for SCD4x (CO2)
- [ ] Mock sensor framework for SHT30 (Temp/Humidity)
- [ ] Mock sensor framework for LD2450/LD2412 (Presence)
- [ ] End-to-end scenario tests
  - [ ] Sensor initialization → reading → status update → LED change
  - [ ] Calibration workflow (reference → compute → apply → verify)
  - [ ] Night mode transition (day → night → day)
  - [ ] Presence detection scenarios (enter → occupy → leave)
- [ ] State machine validation tests
  - [ ] Air quality state transitions
  - [ ] LED animation state machine
  - [ ] Presence zone state tracking
- [ ] Error recovery scenarios
  - [ ] Sensor disconnection/reconnection
  - [ ] WiFi disconnection handling
  - [ ] Invalid sensor readings (NaN, overflow)

**Success Criteria:**
- 50+ integration tests passing
- All 10 product configurations validated
- Error recovery documented and tested

---

### 1.2 Phase 3: CI/CD Pipeline Enhancement
**Effort**: 1 week
**Status**: Partially Complete (GitHub Actions exist)

**Deliverables:**
- [x] GitHub Actions workflow for unit tests
- [x] YAML validation for all configs
- [x] ESPHome compilation check
- [ ] Code coverage reporting (target: 90%+)
- [ ] Integration test automation
- [ ] Automated release tagging
- [ ] Performance benchmarks (compile time, binary size)
- [ ] Slack/Discord notifications on failure

**Success Criteria:**
- All PRs require passing CI
- Coverage reports on every commit
- Automated release notes generation

---

### 1.3 Phase 4: Hardware-in-Loop Testing Setup
**Effort**: 2-3 weeks (initial setup)
**Status**: Not Started

**Deliverables:**
- [ ] Physical test rig design document
- [ ] Automated environmental control (temperature chamber)
- [ ] Sensor calibration verification fixtures
- [ ] LED color/brightness measurement
- [ ] Presence detection validation setup
- [ ] Regression test suite for hardware
- [ ] Nightly hardware test runs

**Success Criteria:**
- Automated hardware tests running nightly
- Regression detection within 24 hours

---

## P2: Core Product Features (User-Facing Value)

Features that directly improve user experience and product capabilities.

### 2.1 Energy Monitoring Integration
**Effort**: 1-2 weeks
**Status**: Mentioned in v2.0.0, needs implementation verification

**Deliverables:**
- [ ] Power consumption sensor (ESP32 measurement)
- [ ] Energy usage tracking (kWh accumulator)
- [ ] Daily/weekly/monthly energy statistics
- [ ] Home Assistant energy dashboard integration
- [ ] Power-saving mode implementation
- [ ] Wake-on-presence feature

**Files to Create/Modify:**
- `features/energy_monitoring.yaml`
- `packages/energy_sensors.yaml`

**Success Criteria:**
- Energy data visible in Home Assistant Energy dashboard
- Accurate power measurement (±5%)

---

### 2.2 Multi-Device Synchronization
**Effort**: 2-3 weeks
**Status**: Mentioned in v2.0.0, needs implementation verification

**Deliverables:**
- [ ] ESPNow mesh communication between devices
- [ ] Presence tracking synchronization across rooms
- [ ] Air quality baseline alignment
- [ ] Coordinated LED status display
- [ ] Master/follower device roles
- [ ] Fallback for network disconnection

**Files to Create/Modify:**
- `features/multi_device_sync.yaml`
- `packages/espnow_mesh.yaml`

**Success Criteria:**
- < 100ms latency for presence sync
- Graceful degradation when mesh unavailable

---

### 2.3 Advanced Air Quality Trending
**Effort**: 1-2 weeks
**Status**: Mentioned in v2.0.0, needs implementation verification

**Deliverables:**
- [ ] Rolling averages (1hr, 4hr, 24hr)
- [ ] Trend indicators (improving/stable/worsening)
- [ ] Historical data retention (7 days on-device)
- [ ] Air quality forecasting (simple ML model)
- [ ] Anomaly detection alerts
- [ ] Export to InfluxDB/Prometheus

**Files to Create/Modify:**
- `features/air_quality_trending.yaml`
- `packages/statistics_sensors.yaml`

**Success Criteria:**
- Accurate trend predictions
- Useful anomaly alerts (low false positive rate)

---

### 2.4 BSEC2 Calibration System
**Effort**: 1-2 weeks
**Status**: BME680 removed, evaluate if needed

**Deliverables:**
- [ ] Evaluate BSEC2 library integration
- [ ] IAQ (Indoor Air Quality) index calculation
- [ ] Calibration state persistence
- [ ] Calibration UI in Home Assistant
- [ ] Calibration quality indicators

**Decision Point:** Determine if BME680/BSEC2 should be re-added or permanently removed.

---

## P3: Enhancement Features (Polish & Differentiation)

Features that improve existing functionality and user experience.

### 3.1 Basic/Advanced Profile Expansion
**Effort**: 2 weeks
**Status**: Partially implemented

**Deliverables:**
- [ ] Complete Basic profile for all product types
  - [ ] Simplified entity exposure
  - [ ] Essential controls only
  - [ ] User-friendly naming
- [ ] Complete Advanced profile for all product types
  - [ ] Full sensor data exposure
  - [ ] Calibration controls
  - [ ] Debug information
  - [ ] Threshold customization
- [ ] Profile switching mechanism (without reflash)
- [ ] Documentation for each profile

**Success Criteria:**
- Clear differentiation between Basic and Advanced
- Easy upgrade path from Basic to Advanced

---

### 3.2 LD2412 Presence Sensor Full Support
**Effort**: 1-2 weeks
**Status**: Partially implemented (configs exist)

**Deliverables:**
- [ ] Complete feature parity with LD2450
- [ ] LD2412-specific calibration
- [ ] Zone configuration for LD2412
- [ ] Performance comparison documentation
- [ ] Migration guide from LD2450 to LD2412

**Success Criteria:**
- All LD2450 features available for LD2412
- Clear guidance on sensor selection

---

### 3.3 LED Animation System Enhancement
**Effort**: 1 week
**Status**: Basic implementation exists

**Deliverables:**
- [ ] Custom animation patterns (breathe, pulse, rainbow)
- [ ] Animation speed control
- [ ] Color palette customization
- [ ] Animation for specific events (CO2 spike, presence detected)
- [ ] Animation editor UI concept

**Success Criteria:**
- 5+ animation patterns available
- User can customize animations via Home Assistant

---

### 3.4 Voice Assistant Integration
**Effort**: 1-2 weeks
**Status**: Not started

**Deliverables:**
- [ ] ESPHome voice assistant component integration
- [ ] Air quality voice queries ("What's the CO2 level?")
- [ ] Presence voice feedback
- [ ] Wake word detection (optional)
- [ ] Local voice processing (no cloud)

**Success Criteria:**
- Basic voice queries working
- < 2 second response time

---

### 3.5 Mobile App / Web Dashboard
**Effort**: 2-3 weeks
**Status**: Not started

**Deliverables:**
- [ ] ESPHome web interface customization
- [ ] Mobile-friendly dashboard
- [ ] Quick actions (calibrate, reset, toggle modes)
- [ ] Historical charts
- [ ] Device health overview

**Success Criteria:**
- Functional standalone web interface
- Works without Home Assistant

---

## P4: Long-term Infrastructure (Ongoing)

Continuous improvement and maintenance tasks.

### 4.1 Documentation & Examples
**Effort**: Ongoing
**Status**: Good foundation exists

**Deliverables:**
- [ ] Video tutorials for installation
- [ ] Troubleshooting decision tree
- [ ] FAQ document
- [ ] Use case examples with complete configs
- [ ] API documentation (auto-generated)
- [ ] Architecture diagrams

---

### 4.2 Performance Optimization
**Effort**: Ongoing
**Status**: Not started

**Deliverables:**
- [ ] Memory usage optimization
- [ ] WiFi reconnection speed
- [ ] Sensor polling efficiency
- [ ] LED update rate optimization
- [ ] Binary size reduction

---

### 4.3 Security Hardening
**Effort**: 1-2 weeks
**Status**: Basic security exists

**Deliverables:**
- [ ] Security audit of current implementation
- [ ] Encrypted OTA updates
- [ ] API authentication improvements
- [ ] Secure boot evaluation
- [ ] Penetration testing

---

### 4.4 Localization / Internationalization
**Effort**: 1-2 weeks
**Status**: Not started

**Deliverables:**
- [ ] Entity name translations
- [ ] Documentation translations
- [ ] Unit preferences (Celsius/Fahrenheit, µg/m³ vs AQI)

---

## Implementation Order (Recommended)

```
Week 1-2:   P1.2 - CI/CD Enhancement (foundation for all other work)
Week 3-6:   P1.1 - Integration Testing (parallel with feature work)
Week 4-5:   P2.1 - Energy Monitoring
Week 6-7:   P2.3 - Air Quality Trending
Week 8-10:  P2.2 - Multi-Device Synchronization
Week 8-9:   P3.1 - Basic/Advanced Profile Expansion
Week 10-11: P3.2 - LD2412 Full Support
Week 11-12: P3.3 - LED Animation Enhancement
Week 12+:   P1.3 - Hardware-in-Loop Testing Setup
Ongoing:    P4.x - Infrastructure improvements
```

---

## Version Planning

### v2.2.0 (Target: +4 weeks)
- P1.2 CI/CD Enhancement
- P2.1 Energy Monitoring
- P3.1 Basic/Advanced Profile Expansion

### v2.3.0 (Target: +8 weeks)
- P1.1 Integration Testing (partial)
- P2.3 Air Quality Trending
- P3.2 LD2412 Full Support

### v3.0.0 (Target: +12 weeks)
- P1.1 Integration Testing (complete)
- P2.2 Multi-Device Synchronization
- P3.3 LED Animation Enhancement
- P3.4 Voice Assistant Integration (experimental)

### v3.1.0+ (Future)
- P1.3 Hardware-in-Loop Testing
- P3.5 Mobile App / Web Dashboard
- P4.x Infrastructure improvements

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Unit Tests | 133 | 200+ |
| Integration Tests | 0 | 50+ |
| Test Coverage | ~95% | 95%+ |
| Product Configs | 10 | 12+ |
| Documentation Pages | 10 | 20+ |
| Average Bug Fix Time | Unknown | < 48 hours |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hardware supply issues | High | Document alternative sensors |
| ESPHome breaking changes | Medium | Pin ESPHome versions, test upgrades |
| Scope creep | Medium | Strict prioritization, MVP focus |
| Technical debt | Medium | Continuous refactoring, code review |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-04 | Prioritize testing before features | Prevent regressions, ensure quality |
| 2025-12-04 | Energy monitoring as first P2 feature | High user demand, clear value |
| TBD | BSEC2 re-evaluation needed | Was removed, assess if needed |

---

## References

- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [Phase 1 Complete](../tests/PHASE1_COMPLETE.md) - Testing status
- [Development Guide](development.md) - Contribution guidelines
- [Configuration Reference](configuration.md) - Feature documentation

---

**Document Owner**: Development Team
**Last Updated**: 2025-12-04
**Next Review**: Weekly during active development

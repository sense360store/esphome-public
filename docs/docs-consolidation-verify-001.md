# DOCS-CONSOLIDATION-VERIFY-001 — Consolidated docs & redirect verification

**Canonical id:** `DOCS-CONSOLIDATION-VERIFY-001`
**Type:** Docs only. This record verifies the existing consolidated docs and
redirect banners. It does **not** change firmware, enable WebFlash, publish
artifacts, edit `manifest.json` / `firmware/sources.json`, promote any product,
or move any readiness gate. No source-of-truth value is changed — every status
statement is read back from a committed config, a test, or a canonical doc.

This is the verification pass for `DOCS-CONSOLIDATION-ROADMAP-001`
([`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md)) and the
WebFlash-side `WEBFLASH-DOCS-CONSOLIDATION-SENSE360-001`
(`docs/sense360-webflash-status.md` in `sense360store/WebFlash`). It confirms
the canonical docs are linked correctly, the superseded docs redirect cleanly,
and no stale product / status claim remains.

## Scope

- `sense360store/esphome-public` (canonical roadmap/status doc + redirects)
- `sense360store/WebFlash` docs references (verified against the local checkout)

## Verification results

| # | Check | Result |
|---|---|---|
| 1 | `README.md` links to the canonical roadmap doc | **PASS** — `README.md:6` → [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md) |
| 2 | `UPCOMING_PR.md` links to the canonical roadmap doc | **PASS** — `UPCOMING_PR.md:11` → [`docs/sense360-roadmap-status.md`](sense360-roadmap-status.md), labelled as the high-level snapshot with this file as the detailed queue |
| 3 | `docs/sense360-roadmap-status.md` internal links resolve | **PASS** — every relative link resolves to an existing file |
| 4 | `docs/sense360-webflash-status.md` reference text accurate | **PASS** — upstream/downstream split correct; every relative link resolves |
| 5 | No stale FanPWM WebFlash / release claim | **PASS** — FanPWM stays `hardware-pending`, no WebFlash token / artifact / build-matrix flip; `S360-311` stays `cataloged_unverified` |
| 6 | No LED-stable claim | **PASS** — all LED references are preview-only / gated behind `RELEASE-007` + `S360-300-BENCH-001`; no positive stable assertion |
| 7 | No S360-410-verified claim | **PASS** — S360-410 stays `cataloged_unverified`; all `verified` mentions are blocked/precondition context |
| 8 | No old SX1509 active FanPWM-path claim | **PASS** — SX1509 path is classified legacy / superseded; native ESP32-S3 GPIO is the active path |
| 9 | Release targets match `config/webflash-builds.json` | **PASS** — exactly two builds: `Ceiling-POE-VentIQ-RoomIQ` (stable, v1.0.0) and `Ceiling-POE-VentIQ-RoomIQ-LED` (preview, v1.0.0) |
| 10 | WebFlash docs show only supported / release-selectable products | **PASS** — `manifest.json` has 3 builds (Release-One stable + LED preview + Rescue); `REQUIRED_CONFIGS = ["Ceiling-POE-VentIQ-RoomIQ", "Rescue"]` (production-only); `FEATURES.md` redirects to the canonical status doc |
| 11 | Superseded docs carry redirect banners | **PASS** — all 8 docs in [§10](sense360-roadmap-status.md#10-consolidated--redirected-docs) carry the canonical redirect banner |

### Redirect banners verified

All eight superseded docs carry the
`⚠️ Superseded for current-state status by docs/sense360-roadmap-status.md
(DOCS-CONSOLIDATION-ROADMAP-001)` banner:

- [`docs/repo-freshness-roadmap-audit.md`](repo-freshness-roadmap-audit.md)
- [`docs/repo-structure-audit.md`](repo-structure-audit.md)
- [`docs/cleanup-audit.md`](cleanup-audit.md)
- [`docs/webflash-drift-audit.md`](webflash-drift-audit.md)
- [`docs/webflash-ci-alignment.md`](webflash-ci-alignment.md)
- [`docs/webflash-release-handoff.md`](webflash-release-handoff.md)
- [`docs/stable-target-expansion-plan.md`](stable-target-expansion-plan.md)
- [`docs/stable-target-ventiq-001-gate-closure.md`](stable-target-ventiq-001-gate-closure.md)

## Test evidence

All validation commands pass on this branch (read-only verification, no source
changed):

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | 210 files checked, 0 failed |
| `python3 tests/test_roadmap_status_doc.py` | 15 tests, OK |
| `python3 tests/test_native_fanpwm_yaml.py` | 31 tests, OK |
| `python3 tests/test_pwm_product_readiness.py` | 74 tests, OK |
| `python3 tests/validate_webflash_builds.py` | 2 builds checked, 0 failed |
| `python3 -m unittest discover -s tests -p "test_*.py"` | 1141 tests, OK (3 skipped) |

## Hard guardrails honoured

No firmware changed · WebFlash not enabled · no artifact published ·
`manifest.json` unchanged · `firmware/sources.json` unchanged · no product
promoted. This record is additive documentation only.

## Conclusion

The consolidated roadmap/status docs are correctly linked from `README.md` and
`UPCOMING_PR.md`, the eight superseded docs redirect cleanly to the canonical
doc, the WebFlash-side status doc reference text is accurate, and no stale
FanPWM / LED-stable / S360-410-verified / SX1509-active-path claim remains.
Release targets match `config/webflash-builds.json`, and the WebFlash surfaces
expose only supported / release-selectable products. **DOCS-CONSOLIDATION-VERIFY-001:
verified.**

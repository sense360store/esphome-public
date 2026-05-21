#!/usr/bin/env python3
"""Generate the firmware build-gap report (FW-MATRIX-002).

This script reads the generated firmware combination readiness matrix at
``config/firmware-combination-matrix.json`` (produced by
``scripts/generate_firmware_matrix.py``) and groups every row into a
practical implementation lane so future PRs can pick build / package /
product work in priority order rather than randomly.

The output is a Markdown report at ``docs/firmware-build-gap-report.md``.
The report is **planning / reporting only** — it never adds firmware
builds, product YAMLs, WebFlash wrappers, artifacts, releases, or
exposure, and it never promotes any combination's status. The two
committed WebFlash builds (``Ceiling-POE-VentIQ-RoomIQ`` stable and
``Ceiling-POE-VentIQ-RoomIQ-LED`` preview) stay verbatim. See
``docs/firmware-build-gap-report.md`` for the per-lane gating rules.

Run with::

    python3 scripts/report_firmware_build_gaps.py

Add ``--check`` to verify the on-disk report matches the regenerated
report without writing. ``--check`` exits non-zero if the report is
stale relative to the matrix or to this script's lane policies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
REPORT_PATH = REPO_ROOT / "docs" / "firmware-build-gap-report.md"

WEBFLASH_STATUSES = frozenset({"webflash-shipping", "webflash-preview"})
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

# Number of representative config strings to surface per lane in the
# Markdown report. The report shows the first N alphabetically; the
# whole row set is still available via the matrix JSON.
REPRESENTATIVES_PER_LANE = 5


def _row_in_webflash_builds(row: Dict[str, Any]) -> bool:
    return row.get("status") in WEBFLASH_STATUSES


def _row_has_fan(row: Dict[str, Any], fan: str) -> bool:
    return row.get("fan") == fan


def _row_power_is(row: Dict[str, Any], power: str) -> bool:
    return row.get("power") == power


def _row_has_led(row: Dict[str, Any]) -> bool:
    return row.get("led") == "LED"


# Lane policies. Each lane has:
#  - id: machine-readable lane identifier
#  - title: human-readable title used in the report
#  - matches(row): predicate; rows are assigned to the first lane that
#    matches in policy order
#  - blocker_summary: prose blocker description for the report
#  - recommended_next_pr: prose recommendation for the next PR type
#  - compile_only_safe_now: bool; True only if compile-only coverage is
#    safe before any further evidence lands
#  - webflash_exposure_allowed_now: bool; True only if the rows in this
#    lane are already in config/webflash-builds.json (the test fixture
#    enforces this — see test_no_lane_implies_unsafe_webflash_exposure)
#  - stable_ready_now: bool; True only if the lane carries a row that is
#    already on the stable channel. LED stable is intentionally False
#    until S360-300-BENCH-001 closes and WebFlash operator proof
#    WF-HW-TEST-001 is filled in.
LANE_POLICIES: List[Dict[str, Any]] = [
    {
        "id": "current-webflash",
        "title": "Current WebFlash builds",
        "matches": _row_in_webflash_builds,
        "blocker_summary": (
            "None for these two rows specifically — they are the only "
            "combinations committed to `config/webflash-builds.json`. "
            "Release-One stable (`Ceiling-POE-VentIQ-RoomIQ`) and the LED "
            "preview (`Ceiling-POE-VentIQ-RoomIQ-LED`)."
        ),
        "recommended_next_pr": (
            "No new build PR for these two rows. Preserve both committed "
            "entries verbatim. Promotion of the LED preview to stable "
            "requires the full 17-row gauntlet in "
            "`docs/preview-to-stable-promotion-gates.md`, including "
            "`S360-300-BENCH-001` bench evidence and the WebFlash "
            "operator-proof container `WF-HW-TEST-001`."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": True,
        "stable_ready_now": False,
        "notes": (
            "`Ceiling-POE-VentIQ-RoomIQ` is the only `stable`-channel "
            "build; `Ceiling-POE-VentIQ-RoomIQ-LED` is `preview` only. "
            "Stable LED promotion remains blocked by S360-300-BENCH-001 "
            "Open Questions (harness rail, LED count, harness identity) "
            "and the WebFlash operator-proof container `WF-HW-TEST-001`."
        ),
    },
    {
        "id": "fantriac-blocked-hardware-compliance",
        "title": "FanTRIAC — blocked on hardware + compliance",
        "matches": lambda r: _row_has_fan(r, "FanTRIAC"),
        "blocker_summary": (
            "FanTRIAC (S360-320) blocked under **HW-005**: S360-320 "
            "schematic is uncommitted; placeholder GPIO5 / GPIO6 collide "
            "with RoomIQ J10 nets; ESPHome `ac_dimmer` cannot run across "
            "the SX1509 expander. Also blocked under **HW-PINMAP-320-FOLLOWUP** "
            "(audit partial), **PACKAGE-TRIAC-001** (package deferred), "
            "and **COMPLIANCE-001** (mains-voltage advanced / manual-warning "
            "sign-off open)."
        ),
        "recommended_next_pr": (
            "No FanTRIAC build, package, or product PR. The catalog entry "
            "for `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` stays "
            "`status: blocked` / `blocker: HW-005`. Subsequent PRs are "
            "evidence-pass investigations only until HW-005 + "
            "COMPLIANCE-001 close. See "
            "`docs/release-one-hardware-audit.md#fantriac-mapping-resolution`."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "All 36 FanTRIAC rows inherit the same HW-005 blocker via the "
            "token-level inference in `scripts/generate_firmware_matrix.py`. "
            "Mains-voltage handling means FanTRIAC additionally needs "
            "compliance sign-off before any preview-class WebFlash "
            "exposure can even be considered."
        ),
    },
    {
        "id": "fanrelay-blocked-package-or-core-bus",
        "title": "FanRelay — blocked on package + Core abstract bus",
        "matches": lambda r: _row_has_fan(r, "FanRelay"),
        "blocker_summary": (
            "FanRelay (S360-310) blocked behind **PACKAGE-RELAY-001** "
            "(deferred) and **CORE-ABSTRACT-BUS-001A** (which is itself "
            "blocked behind **CORE-ABSTRACT-BUS-001C** due to a `GPIO3` "
            "collision). Still owed: silkscreen / harness / `K1` BOM "
            "evidence for `S360-310`; ESP32-S3 `GPIO3` strap-pin "
            "boot-behaviour bench characterisation; `S360-100-BENCH-001`; "
            "a `tests/test_core_abstract_bus.py` pin-pinning scaffold."
        ),
        "recommended_next_pr": (
            "No FanRelay build or product PR. Implementation chain is "
            "**CORE-ABSTRACT-BUS-001C → CORE-ABSTRACT-BUS-001A → "
            "PACKAGE-RELAY-001 → PRODUCT-RELAY-001 → WEBFLASH-RELAY-001 → "
            "RELEASE-RELAY-001**. Stay on docs-only investigation passes "
            "until 001A lands together with the listed evidence."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "`packages/expansions/fan_relay.yaml` cannot be safely edited "
            "until CORE-ABSTRACT-BUS-001A frees `GPIO3` and the bench / "
            "silkscreen / BOM evidence lands. Compile-only coverage is "
            "**not** safe yet because the abstract-bus rebind would "
            "change the consumed substitution names."
        ),
    },
    {
        "id": "fanpwm-blocked-package-or-core-bus",
        "title": "FanPWM — blocked on package + Core abstract bus",
        "matches": lambda r: _row_has_fan(r, "FanPWM"),
        "blocker_summary": (
            "FanPWM (S360-311) blocked behind **PACKAGE-PWM-001** "
            "(deferred) and **CORE-ABSTRACT-BUS-001B** (canonical I²C "
            "bus-id consolidation). Still owed: BOM evidence "
            "(`HW-BOM-ASSETS-S360-311`); further `HW-PINMAP-311-FOLLOWUP` "
            "evidence; `tests/test_core_abstract_bus.py` pin-pinning "
            "scaffold; canonical I²C bus-id decision."
        ),
        "recommended_next_pr": (
            "No FanPWM build or product PR. Implementation chain is "
            "**CORE-ABSTRACT-BUS-001B → PACKAGE-PWM-001 → PRODUCT-PWM-001 → "
            "WEBFLASH-PWM-001 → RELEASE-PWM-001**. Stay on docs-only "
            "investigation passes until 001B lands."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "`packages/expansions/fan_pwm.yaml` consumes `expansion_gpio1` "
            "/ `expansion_gpio2`, so the abstract-bus rebind in 001B / "
            "001C must complete before any product-level edits are safe."
        ),
    },
    {
        "id": "fandac-blocked-package-or-core-bus",
        "title": "FanDAC — blocked on package + Core abstract bus",
        "matches": lambda r: _row_has_fan(r, "FanDAC"),
        "blocker_summary": (
            "FanDAC (S360-312) blocked behind **PACKAGE-DAC-001** "
            "(deferred) and **CORE-ABSTRACT-BUS-001B** (canonical I²C "
            "bus-id consolidation; the GP8403 DAC is an I²C peripheral). "
            "Still owed: BOM evidence (`HW-BOM-ASSETS-S360-312`); further "
            "`HW-PINMAP-312-FOLLOWUP` evidence; `tests/test_core_abstract_bus.py` "
            "pin-pinning scaffold. FanDAC + AirIQ is forbidden by the "
            "grammar (12 rows excluded from the matrix), so this lane "
            "carries 24 rows."
        ),
        "recommended_next_pr": (
            "No FanDAC build or product PR. Implementation chain is "
            "**CORE-ABSTRACT-BUS-001B → PACKAGE-DAC-001 → PRODUCT-DAC-001 → "
            "WEBFLASH-DAC-001 → RELEASE-DAC-001**. Stay on docs-only "
            "investigation passes until 001B lands."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "`packages/expansions/fan_gp8403.yaml` consumes the "
            "to-be-consolidated I²C bus-id. Compile-only coverage cannot "
            "be added safely before the canonical bus-id is chosen."
        ),
    },
    {
        "id": "pwr-blocked-compliance",
        "title": "PWR-240V — blocked on compliance",
        "matches": lambda r: _row_power_is(r, "PWR"),
        "blocker_summary": (
            "PWR-240V (S360-400) blocked under **COMPLIANCE-001** "
            "(mains-voltage UK / EU advanced / manual-warning sign-off "
            "open) and behind **PACKAGE-POWER-400-001** / "
            "**PRODUCT-POWER-400-001** / **WEBFLASH-POWER-400-001** / "
            "**RELEASE-POWER-400-001**. `S360-400` is "
            "`schematic_status: cataloged_unverified` "
            "(HW-PINMAP-400-FOLLOWUP partial; the schematic PDF's "
            "`PS1 = HLK-10M05` value-field discrepancy still unresolved)."
        ),
        "recommended_next_pr": (
            "No PWR build, package, or product PR. Subsequent PRs are "
            "docs-only investigation passes until COMPLIANCE-001 closes "
            "and `S360-400` is `schematic_status: verified`. WebFlash "
            "exposure for mains-voltage power is **not** allowed under "
            "any channel without a qualified electrical-safety review."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "PWR-240V touches mains voltage. Documentation alone is not "
            "sufficient to clear compliance; a qualified electrical-safety "
            "/ compliance review recorded outside this repo is required."
        ),
    },
    {
        "id": "led-preview-and-stable-candidates",
        "title": "LED preview / stable candidates (non-fan, non-PWR)",
        "matches": lambda r: _row_has_led(r) and not _row_in_webflash_builds(r),
        "blocker_summary": (
            "LED-bearing combinations on POE / USB power that are not yet "
            "in `config/webflash-builds.json`. Blocked from preview "
            "exposure by missing product YAML, missing WebFlash wrapper, "
            "and missing catalog entries. Blocked from **stable** "
            "promotion by `S360-300-BENCH-001` (harness rail, LED count, "
            "harness identity Open Questions remain `verify`) and the "
            "WebFlash operator-proof container `WF-HW-TEST-001` "
            "(not yet filled)."
        ),
        "recommended_next_pr": (
            "No LED build PR for these rows. Compile-only coverage may "
            "become safe **after** the per-power product family (POE-410 "
            "/ USB-power) clears its own gates; until then keep LED "
            "candidates as docs-only readiness rows. Stable promotion of "
            "*any* LED build requires S360-300-BENCH-001 to close and "
            "`WF-HW-TEST-001` to be filled — neither has happened yet."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "`S360-300` is `schematic_status: verified` (HW-007 / HW-008), "
            "but stable readiness requires bench evidence and an "
            "operator-flash proof in addition to package + product + "
            "wrapper + build + release proof for the **specific** "
            "config string."
        ),
    },
    {
        "id": "poe-non-fan-candidates",
        "title": "POE non-fan candidates",
        "matches": lambda r: _row_power_is(r, "POE") and not _row_has_led(r),
        "blocker_summary": (
            "POE (S360-410) candidates without a fan and without LED, "
            "excluding `Ceiling-POE-VentIQ-RoomIQ` (already shipping). "
            "`S360-410` is `schematic_status: cataloged_unverified` "
            "(HW-PINMAP-410-FOLLOWUP partial). **PACKAGE-POE-410-001** / "
            "**PRODUCT-POE-410-001** / **WEBFLASH-POE-410-001** / "
            "**RELEASE-POE-410-001** all blocked behind BOM cross-check, "
            "`schematic_status: verified` JSON PR, HW-002 OQ#6, "
            "`S360-100-BENCH-001` J2-harness identity closure, "
            "Release-One PoE caveat closure, product-onboarding approval."
        ),
        "recommended_next_pr": (
            "No POE non-fan product or build PR for these rows. They are "
            "documented as readiness-tracking placeholders; the catalog "
            "carries no product YAML for them today. Wait for the "
            "PACKAGE/PRODUCT/WEBFLASH/RELEASE-POE-410-001 chain to "
            "complete before any compile-only or preview-class work."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "These rows are valid grammar combinations but have no "
            "product YAML in `config/product-catalog.json` and no entry "
            "in `config/webflash-builds.json`. They are tracking entries "
            "only, not requests to add a product."
        ),
    },
    {
        "id": "usb-non-fan-candidates",
        "title": "USB non-fan candidates",
        "matches": lambda r: _row_power_is(r, "USB") and not _row_has_led(r),
        "blocker_summary": (
            "USB-powered candidates without a fan and without LED. The "
            "catalog has no S360-* USB PSU board entry and no S360-* USB "
            "product family. USB on `S360-100` is debug-only per the "
            "catalog. No `PACKAGE-USB-*` / `PRODUCT-USB-*` / "
            "`WEBFLASH-USB-*` / `RELEASE-USB-*` chain has been opened."
        ),
        "recommended_next_pr": (
            "No USB product or build PR. USB-family product onboarding "
            "has not been opened; readiness-tracking only until a "
            "deliberate USB-family scope decision is recorded. "
            "Compile-only coverage cannot bypass the missing PSU / "
            "harness / catalog evidence."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "Until a USB-family scope decision is documented, these rows "
            "are tracking entries only. No compile-only build or product "
            "YAML is added by this report."
        ),
    },
    {
        "id": "missing-product-yaml",
        "title": "Missing-product-yaml (sentinel)",
        "matches": lambda r: True,  # catch-all
        "blocker_summary": (
            "Sentinel lane for rows that do not match any specific lane "
            "above. With the current matrix and lane policies this lane "
            "is empty; it is retained so any future grammar drift "
            "(`config/webflash-compatibility.json`) or new combination "
            "shape is forced into an explicit lane by an explicit "
            "follow-up PR rather than silently disappearing."
        ),
        "recommended_next_pr": (
            "If this lane is non-empty in a future run, open a follow-up "
            "PR to extend the lane policies in "
            "`scripts/report_firmware_build_gaps.py`. Do not promote any "
            "row to a more permissive lane without explicit evidence."
        ),
        "compile_only_safe_now": False,
        "webflash_exposure_allowed_now": False,
        "stable_ready_now": False,
        "notes": (
            "An empty sentinel lane is the expected steady state; a "
            "non-empty value indicates either matrix grammar drift or a "
            "stale lane policy."
        ),
    },
]


def assign_lane(row: Dict[str, Any]) -> str:
    """Assign one matrix row to exactly one lane.

    The first lane in ``LANE_POLICIES`` whose ``matches`` predicate
    returns True wins. The final lane (``missing-product-yaml``) is a
    catch-all whose predicate is unconditionally True; that guarantees
    every row is covered.
    """
    for lane in LANE_POLICIES:
        if lane["matches"](row):
            return lane["id"]
    # The catch-all lane ensures this is unreachable; defensive only.
    raise RuntimeError(f"row {row.get('config_string')!r} did not match any lane")


def group_by_lane(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group every matrix row into its assigned lane.

    Returns a mapping lane_id -> sorted list of rows (sorted by
    config_string for stable Markdown output).
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {
        lane["id"]: [] for lane in LANE_POLICIES
    }
    for row in rows:
        lane_id = assign_lane(row)
        grouped[lane_id].append(row)
    for lane_id, lane_rows in grouped.items():
        lane_rows.sort(key=lambda r: r["config_string"])
    return grouped


def _committed_build_config_strings(builds_doc: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for entry in builds_doc.get("builds", []) or []:
        cs = entry.get("config_string")
        if isinstance(cs, str):
            out.append(cs)
    return sorted(out)


def build_lane_report_entries(
    grouped: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Build the per-lane report entries in policy order."""
    out: List[Dict[str, Any]] = []
    for lane in LANE_POLICIES:
        lane_rows = grouped[lane["id"]]
        reps = [r["config_string"] for r in lane_rows[:REPRESENTATIVES_PER_LANE]]
        out.append(
            {
                "id": lane["id"],
                "title": lane["title"],
                "count": len(lane_rows),
                "representatives": reps,
                "blocker_summary": lane["blocker_summary"],
                "recommended_next_pr": lane["recommended_next_pr"],
                "compile_only_safe_now": lane["compile_only_safe_now"],
                "webflash_exposure_allowed_now": lane["webflash_exposure_allowed_now"],
                "stable_ready_now": lane["stable_ready_now"],
                "notes": lane["notes"],
                "config_strings": [r["config_string"] for r in lane_rows],
            }
        )
    return out


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _format_lane_section(entry: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(
        f"### `{entry['id']}` — {entry['title']} ({entry['count']} rows)"
    )
    lines.append("")
    lines.append(
        f"- **Compile-only coverage safe now:** {_yes_no(entry['compile_only_safe_now'])}"
    )
    lines.append(
        f"- **WebFlash exposure allowed now:** {_yes_no(entry['webflash_exposure_allowed_now'])}"
    )
    lines.append(
        f"- **Stable-ready now:** {_yes_no(entry['stable_ready_now'])}"
    )
    lines.append("")
    lines.append(f"**Blocker summary.** {entry['blocker_summary']}")
    lines.append("")
    lines.append(f"**Recommended next PR type.** {entry['recommended_next_pr']}")
    lines.append("")
    lines.append(f"**Notes.** {entry['notes']}")
    lines.append("")
    if entry["count"] == 0:
        lines.append("**Representative config strings.** (none — lane is empty.)")
    else:
        lines.append("**Representative config strings.**")
        lines.append("")
        for cs in entry["representatives"]:
            lines.append(f"- `{cs}`")
        if entry["count"] > len(entry["representatives"]):
            remaining = entry["count"] - len(entry["representatives"])
            lines.append(
                f"- … and {remaining} more (see "
                "`config/firmware-combination-matrix.json` for the full list)"
            )
    lines.append("")
    return "\n".join(lines)


def render_report(
    matrix: Dict[str, Any],
    lane_entries: List[Dict[str, Any]],
    builds: Dict[str, Any],
) -> str:
    """Render the full Markdown report from the lane entries."""
    total = matrix.get("totals", {}).get("combinations", 0)
    by_status = matrix.get("totals", {}).get("by_status", {}) or {}
    committed = _committed_build_config_strings(builds)
    lane_total = sum(entry["count"] for entry in lane_entries)

    lines: List[str] = []
    lines.append("# Firmware Build Gap Report (FW-MATRIX-002)")
    lines.append("")
    lines.append("## Purpose and scope")
    lines.append("")
    lines.append(
        "This document is the **generated build-gap report** over the "
        f"{total}-row firmware combination readiness matrix produced by "
        "[`scripts/generate_firmware_matrix.py`](../scripts/generate_firmware_matrix.py). "
        "It groups every valid WebFlash-style combination into a "
        "practical implementation lane so future PRs can pick build / "
        "package / product work in priority order rather than randomly."
    )
    lines.append("")
    lines.append(
        "The report is **planning / reporting only**. It does **not**:"
    )
    lines.append("")
    lines.extend(
        [
            "- build firmware,",
            "- create release artifacts,",
            "- expose new WebFlash builds,",
            "- add `webflash_build_matrix: true` to any product,",
            "- add `artifact_name` to any product,",
            "- promote LED to stable,",
            "- promote any blocked fan module,",
            "- promote `PWR` / `S360-400`,",
            "- promote `POE` / `S360-410`,",
            "- claim hardware proof exists,",
            "- claim `RELEASE-007` is unblocked,",
            "- claim WebFlash import is ready,",
            "- change [`config/webflash-builds.json`](../config/webflash-builds.json),",
            "  [`config/product-catalog.json`](../config/product-catalog.json),",
            "  [`config/hardware-catalog.json`](../config/hardware-catalog.json), or",
            "  [`config/webflash-compatibility.json`](../config/webflash-compatibility.json),",
            "- change `products/**`, `products/webflash/**`, `packages/**`,",
            "  `firmware/**`, `manifest.json`, `firmware/sources.json`,",
            "  `.github/workflows/**`, release artifacts, checksums, or",
            "  build-info manifests,",
            "- change `REQUIRED_CONFIGS`.",
        ]
    )
    lines.append("")
    lines.append("## How the report is generated")
    lines.append("")
    lines.append(
        "The script "
        "[`scripts/report_firmware_build_gaps.py`](../scripts/report_firmware_build_gaps.py) "
        "reads "
        "[`config/firmware-combination-matrix.json`](../config/firmware-combination-matrix.json), "
        "applies a fixed ordered list of lane predicates, and writes this "
        "Markdown report. The first lane whose predicate matches a row "
        "wins; the final `missing-product-yaml` lane is an unconditional "
        "catch-all sentinel."
    )
    lines.append("")
    lines.append("```sh")
    lines.append("python3 scripts/report_firmware_build_gaps.py            # regenerate")
    lines.append("python3 scripts/report_firmware_build_gaps.py --check    # CI-style freshness check")
    lines.append("```")
    lines.append("")
    lines.append("## Source matrix totals")
    lines.append("")
    lines.append(f"- Total valid combinations: **{total}**")
    if by_status:
        for status in sorted(by_status):
            lines.append(f"- `{status}`: {by_status[status]}")
    lines.append("")
    lines.append("## Currently committed WebFlash builds")
    lines.append("")
    lines.append(
        "These are the only combinations in "
        "[`config/webflash-builds.json`](../config/webflash-builds.json) "
        "today. No build, wrapper, artifact, or release is added by this "
        "report."
    )
    lines.append("")
    if committed:
        for cs in committed:
            lines.append(f"- `{cs}`")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Lane summary")
    lines.append("")
    lines.append(
        "| Lane | Rows | Compile-only safe now? | WebFlash exposure allowed now? | Stable-ready now? |"
    )
    lines.append(
        "|------|-----:|------------------------|--------------------------------|--------------------|"
    )
    for entry in lane_entries:
        lines.append(
            "| `{id}` | {count} | {compile_only} | {webflash} | {stable} |".format(
                id=entry["id"],
                count=entry["count"],
                compile_only=_yes_no(entry["compile_only_safe_now"]),
                webflash=_yes_no(entry["webflash_exposure_allowed_now"]),
                stable=_yes_no(entry["stable_ready_now"]),
            )
        )
    lines.append("")
    lines.append(
        f"All {lane_total} lane-assigned rows must equal the {total} "
        "matrix combinations. The test "
        "[`tests/test_firmware_build_gap_report.py`](../tests/test_firmware_build_gap_report.py) "
        "pins this invariant."
    )
    lines.append("")
    lines.append("## Lanes")
    lines.append("")
    for entry in lane_entries:
        lines.append(_format_lane_section(entry))
    lines.append("## Coverage")
    lines.append("")
    lines.append(
        f"All {total} matrix rows are accounted for by exactly one lane. "
        "Subtotals:"
    )
    lines.append("")
    for entry in lane_entries:
        lines.append(f"- `{entry['id']}`: {entry['count']}")
    lines.append("")
    lines.append(f"Sum: **{lane_total}**.")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append(
        "- No lane in this report claims WebFlash exposure is allowed "
        "unless every row in the lane is already committed to "
        "[`config/webflash-builds.json`](../config/webflash-builds.json). "
        "The test "
        "[`tests/test_firmware_build_gap_report.py`](../tests/test_firmware_build_gap_report.py) "
        "enforces this."
    )
    lines.append(
        "- No lane is marked stable-ready. The LED candidate lane "
        "explicitly requires `S360-300-BENCH-001` to close and the "
        "WebFlash operator-proof container `WF-HW-TEST-001` to be filled."
    )
    lines.append(
        "- The FanTRIAC lane references **HW-005** verbatim. The PWR "
        "lane references **COMPLIANCE-001** verbatim. Removing those "
        "references is a deliberate evidence-pass PR, not a side-effect "
        "of this report."
    )
    lines.append(
        "- The `missing-product-yaml` lane is a sentinel: it should be "
        "empty under steady-state. A non-empty value indicates matrix "
        "grammar drift or stale lane policies and requires a follow-up "
        "PR to extend "
        "[`scripts/report_firmware_build_gaps.py`](../scripts/report_firmware_build_gaps.py)."
    )
    lines.append("")
    lines.append("## See also")
    lines.append("")
    lines.append(
        "- [`docs/firmware-combination-matrix.md`](firmware-combination-matrix.md) — FW-MATRIX-001, the source matrix this report consumes."
    )
    lines.append(
        "- [`docs/preview-to-stable-promotion-gates.md`](preview-to-stable-promotion-gates.md) — the 17-row stable-promotion gauntlet that LED candidates must clear."
    )
    lines.append(
        "- [`docs/product-readiness-matrix.md`](product-readiness-matrix.md) — PRODUCT-GAP-001, product-layer readiness."
    )
    lines.append(
        "- [`docs/webflash-exposure-readiness-matrix.md`](webflash-exposure-readiness-matrix.md) — WEBFLASH-GAP-001, WebFlash-exposure readiness."
    )
    lines.append(
        "- [`docs/release-artifact-readiness-matrix.md`](release-artifact-readiness-matrix.md) — RELEASE-GAP-001, release-artifact readiness."
    )
    lines.append(
        "- [`docs/hardware/package-readiness-matrix.md`](hardware/package-readiness-matrix.md) — PACKAGE-GAP-001, package-layer readiness."
    )
    lines.append(
        "- [`docs/release-one-hardware-audit.md`](release-one-hardware-audit.md) — Release-One hardware audit (HW-005 source-of-truth)."
    )
    lines.append("")
    return "\n".join(lines)


def generate(
    matrix: Dict[str, Any],
    builds: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], str]:
    """Return (lane_entries, rendered_markdown) for the given inputs."""
    rows = matrix.get("combinations", []) or []
    grouped = group_by_lane(rows)
    lane_entries = build_lane_report_entries(grouped)
    rendered = render_report(matrix, lane_entries, builds)
    return lane_entries, rendered


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write; exit non-zero if the on-disk report differs "
            "from the regenerated report."
        ),
    )
    args = parser.parse_args(argv)

    if not MATRIX_PATH.exists():
        print(
            f"❌ {MATRIX_PATH.relative_to(REPO_ROOT)} does not exist; "
            "run `python3 scripts/generate_firmware_matrix.py`."
        )
        return 1
    matrix = json.loads(MATRIX_PATH.read_text())
    builds = json.loads(BUILDS_PATH.read_text())

    lane_entries, rendered = generate(matrix, builds)
    total = matrix.get("totals", {}).get("combinations", 0)
    lane_total = sum(entry["count"] for entry in lane_entries)
    if lane_total != total:
        print(
            f"❌ lane row total {lane_total} does not match matrix total "
            f"{total}; lane policies are out of sync with the matrix."
        )
        return 1

    if args.check:
        if not REPORT_PATH.exists():
            print(
                f"❌ {REPORT_PATH.relative_to(REPO_ROOT)} does not exist; "
                "run `python3 scripts/report_firmware_build_gaps.py`."
            )
            return 1
        on_disk = REPORT_PATH.read_text()
        if on_disk != rendered:
            print(
                f"❌ {REPORT_PATH.relative_to(REPO_ROOT)} is stale; "
                "run `python3 scripts/report_firmware_build_gaps.py`."
            )
            return 1
        print(
            f"✅ {REPORT_PATH.relative_to(REPO_ROOT)} is up to date "
            f"({total} matrix rows across {len(lane_entries)} lanes)."
        )
        return 0

    REPORT_PATH.write_text(rendered)
    print(
        f"✅ Wrote {REPORT_PATH.relative_to(REPO_ROOT)} "
        f"({total} matrix rows across {len(lane_entries)} lanes)."
    )
    for entry in lane_entries:
        print(f"    {entry['id']}: {entry['count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

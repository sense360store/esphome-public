#!/usr/bin/env python3
"""Generate the firmware combination readiness matrix.

This script enumerates every valid WebFlash-style config-string combination
defined by ``config/webflash-compatibility.json`` and classifies each one
against ``config/product-catalog.json`` and ``config/webflash-builds.json``.

The output is written to ``config/firmware-combination-matrix.json``. The
generated file is **readiness tracking**, not WebFlash exposure. It does
not build firmware, expose new WebFlash builds, promote products, or
flip ``webflash_build_matrix`` flags. See
``docs/firmware-combination-matrix.md`` for the gating rules.

Run with::

    python3 scripts/generate_firmware_matrix.py

Add ``--check`` to verify the on-disk matrix matches the regenerated
matrix without writing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"

FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

# Status values used in the generated matrix. Documented in
# docs/firmware-combination-matrix.md.
STATUS_WEBFLASH_SHIPPING = "webflash-shipping"
STATUS_WEBFLASH_PREVIEW = "webflash-preview"
STATUS_PRODUCT_EXISTS_NOT_WEBFLASH = "product-exists-not-webflash"
STATUS_COMPILE_ONLY_CANDIDATE = "compile-only-candidate"
STATUS_MISSING_PRODUCT_YAML = "missing-product-yaml"
STATUS_BLOCKED_HARDWARE = "blocked-hardware"
STATUS_BLOCKED_COMPLIANCE = "blocked-compliance"
STATUS_BLOCKED_PACKAGE = "blocked-package"
STATUS_INVALID_BY_GRAMMAR = "invalid-by-grammar"

ALLOWED_STATUSES = frozenset(
    {
        STATUS_WEBFLASH_SHIPPING,
        STATUS_WEBFLASH_PREVIEW,
        STATUS_PRODUCT_EXISTS_NOT_WEBFLASH,
        STATUS_COMPILE_ONLY_CANDIDATE,
        STATUS_MISSING_PRODUCT_YAML,
        STATUS_BLOCKED_HARDWARE,
        STATUS_BLOCKED_COMPLIANCE,
        STATUS_BLOCKED_PACKAGE,
        STATUS_INVALID_BY_GRAMMAR,
    }
)

# Map a catalog blocker identifier to a coarse-grained status.
# Conservative: hardware blockers map to blocked-hardware, compliance to
# blocked-compliance, package to blocked-package.
BLOCKER_STATUS_PREFIXES = (
    ("HW-", STATUS_BLOCKED_HARDWARE),
    ("COMPLIANCE-", STATUS_BLOCKED_COMPLIANCE),
    ("PACKAGE-", STATUS_BLOCKED_PACKAGE),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def is_valid_combination(
    air: Optional[str],
    fan: Optional[str],
    rules: Dict[str, Any],
) -> bool:
    """Apply the slot-level grammar rules from webflash-compatibility.json.

    Config strings enumerated in the compatibility snapshot's
    ``fandac_air_quality_address_policy.address_overridden_exception_config_strings``
    are re-admitted by ``enumerate_combinations`` even when this returns
    False (HW-RELEASE-001 documented address-overridden exception).
    """
    if (
        rules.get("airiq_and_ventiq_mutually_exclusive", True)
        and air == "AirIQ"
        and fan is None
    ):
        # AirIQ alone is fine; only AirIQ+VentIQ would be blocked, but our
        # enumeration uses a single "air" slot so this branch is unreachable.
        # Kept for symmetry / readability.
        pass
    if (
        rules.get("fandac_conflicts_with_airiq", True)
        and air == "AirIQ"
        and fan == "FanDAC"
    ):
        return False
    return True


def build_config_string(
    mounting: str,
    power: str,
    air: Optional[str],
    fan: Optional[str],
    room: Optional[str],
    led: Optional[str],
) -> Tuple[str, List[str]]:
    """Build a config string in the canonical order from the WebFlash contract:

    ``{Mounting}-{Power}-[AirIQ|VentIQ]-[FanRelay|FanPWM|FanDAC|FanTRIAC]-[RoomIQ]-[LED]``
    """
    tokens: List[str] = [mounting, power]
    for slot in (air, fan, room, led):
        if slot is not None:
            tokens.append(slot)
    return "-".join(tokens), tokens


def enumerate_combinations(compat: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Enumerate every valid grammar combination from the compatibility snapshot."""
    rules = compat.get("rules", {})
    mountings = list(compat.get("canonical_mounting", []))
    powers = list(compat.get("canonical_power", []))
    exceptions = set(
        compat.get("fandac_air_quality_address_policy", {}).get(
            "address_overridden_exception_config_strings", []
        )
    )

    air_slots: List[Optional[str]] = [None, "AirIQ", "VentIQ"]
    room_slots: List[Optional[str]] = [None, "RoomIQ"]
    fan_slots: List[Optional[str]] = [None] + list(FAN_DRIVER_TOKENS)
    led_slots: List[Optional[str]] = [None, "LED"]

    out: List[Dict[str, Any]] = []
    for mounting in mountings:
        for power in powers:
            for air in air_slots:
                for fan in fan_slots:
                    slot_valid = is_valid_combination(air, fan, rules)
                    for room in room_slots:
                        for led in led_slots:
                            cs, tokens = build_config_string(
                                mounting, power, air, fan, room, led
                            )
                            if not slot_valid and cs not in exceptions:
                                continue
                            out.append(
                                {
                                    "config_string": cs,
                                    "tokens": tokens,
                                    "mounting": mounting,
                                    "power": power,
                                    "air_quality": air or "none",
                                    "room_sense": room or "none",
                                    "fan": fan or "none",
                                    "led": led or "none",
                                }
                            )
    return out


def _build_index(builds_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index webflash-builds entries by config_string."""
    out: Dict[str, Dict[str, Any]] = {}
    for entry in builds_doc.get("builds", []) or []:
        cs = entry.get("config_string")
        if isinstance(cs, str):
            out[cs] = entry
    return out


def _catalog_index(catalog_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index product-catalog entries by config_string (skip entries without one)."""
    out: Dict[str, Dict[str, Any]] = {}
    for entry in catalog_doc.get("products", []) or []:
        cs = entry.get("config_string")
        if isinstance(cs, str):
            out[cs] = entry
    return out


def _blocker_status(blocker: Optional[str]) -> str:
    """Map a catalog blocker token to one of the blocked-* statuses."""
    if not blocker:
        return STATUS_BLOCKED_HARDWARE
    for prefix, status in BLOCKER_STATUS_PREFIXES:
        if blocker.startswith(prefix):
            return status
    return STATUS_BLOCKED_HARDWARE


def _channel_status(channel: Optional[str]) -> str:
    if channel == "stable":
        return STATUS_WEBFLASH_SHIPPING
    if channel == "preview":
        return STATUS_WEBFLASH_PREVIEW
    # beta / dev / rescue: not promoted to shipping; record as preview-class
    # (still gated by WebFlash). The matrix never invents new statuses.
    return STATUS_WEBFLASH_PREVIEW


def classify(
    combo: Dict[str, Any],
    builds_index: Dict[str, Dict[str, Any]],
    catalog_index: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Classify a single grammar combination against the catalogs.

    Returns the row dict that ends up in the matrix.
    """
    cs = combo["config_string"]
    tokens = combo["tokens"]
    build_entry = builds_index.get(cs)
    catalog_entry = catalog_index.get(cs)

    row: Dict[str, Any] = {
        "config_string": cs,
        "tokens": list(tokens),
        "mounting": combo["mounting"],
        "power": combo["power"],
        "air_quality": combo["air_quality"],
        "room_sense": combo["room_sense"],
        "fan": combo["fan"],
        "led": combo["led"],
    }

    blockers: List[str] = []
    notes_parts: List[str] = []

    if build_entry is not None:
        channel = build_entry.get("channel")
        row["status"] = _channel_status(channel)
        if build_entry.get("product_yaml"):
            row["product_yaml"] = build_entry["product_yaml"]
        if build_entry.get("artifact_name"):
            row["artifact_name"] = build_entry["artifact_name"]
        # webflash_wrapper comes from the catalog when present.
        if catalog_entry and catalog_entry.get("webflash_wrapper"):
            row["webflash_wrapper"] = catalog_entry["webflash_wrapper"]
        notes_parts.append(f"In config/webflash-builds.json on the {channel} channel.")
    elif catalog_entry is not None:
        status = catalog_entry.get("status")
        if status == "blocked":
            blocker = catalog_entry.get("blocker")
            row["status"] = _blocker_status(blocker)
            if blocker:
                blockers.append(blocker)
            reason = catalog_entry.get("reason")
            if reason:
                notes_parts.append(reason)
        elif status in ("production", "preview"):
            row["status"] = STATUS_PRODUCT_EXISTS_NOT_WEBFLASH
            notes_parts.append(
                f"product-catalog status={status} but no entry in "
                "config/webflash-builds.json."
            )
        elif status == "compile-only":
            row["status"] = STATUS_COMPILE_ONLY_CANDIDATE
            notes_parts.append("Catalog status=compile-only.")
        elif status == "hardware-pending":
            row["status"] = STATUS_BLOCKED_HARDWARE
            notes_parts.append("Catalog status=hardware-pending.")
        else:
            row["status"] = STATUS_PRODUCT_EXISTS_NOT_WEBFLASH
            if status:
                notes_parts.append(f"Catalog status={status}.")

        if catalog_entry.get("product_yaml"):
            row["product_yaml"] = catalog_entry["product_yaml"]
        if catalog_entry.get("webflash_wrapper"):
            row["webflash_wrapper"] = catalog_entry["webflash_wrapper"]
        if catalog_entry.get("artifact_name"):
            row["artifact_name"] = catalog_entry["artifact_name"]
    else:
        # No catalog entry and no build entry. Infer from tokens:
        # FanTRIAC family combinations with no catalog/product entry are
        # treated as blocked-hardware (the historical FanTRIAC HW-005
        # buildability gate) as a conservative default. The one catalog
        # bundle (Ceiling-POE-VentIQ-FanTRIAC-RoomIQ) is classified via its
        # own catalog blocker above (PACKAGE-TRIAC-001 + COMPLIANCE-001).
        if "FanTRIAC" in tokens:
            row["status"] = STATUS_BLOCKED_HARDWARE
            blockers.append("HW-005")
            notes_parts.append(
                "FanTRIAC family combination with no catalog/product entry; "
                "blocked-hardware as a conservative default (HW-005)."
            )
        else:
            row["status"] = STATUS_MISSING_PRODUCT_YAML
            notes_parts.append(
                "No product YAML in config/product-catalog.json and no "
                "entry in config/webflash-builds.json."
            )

    if blockers:
        row["blockers"] = blockers
    if notes_parts:
        row["notes"] = " ".join(notes_parts)

    return row


def generate(
    compat: Dict[str, Any],
    builds_doc: Dict[str, Any],
    catalog_doc: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate the full matrix document."""
    combos = enumerate_combinations(compat)
    builds_index = _build_index(builds_doc)
    catalog_index = _catalog_index(catalog_doc)

    rows = [classify(c, builds_index, catalog_index) for c in combos]
    rows.sort(key=lambda r: r["config_string"])

    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    return {
        "schema_version": 1,
        "description": (
            "Generated readiness matrix of every valid WebFlash-style firmware "
            "combination. Source-of-truth grammar: "
            "config/webflash-compatibility.json. Generated by "
            "scripts/generate_firmware_matrix.py. This file is readiness "
            "tracking only; it does not build firmware, expose new WebFlash "
            "builds, or promote any product status. See "
            "docs/firmware-combination-matrix.md."
        ),
        "sources": {
            "compatibility": "config/webflash-compatibility.json",
            "builds": "config/webflash-builds.json",
            "catalog": "config/product-catalog.json",
        },
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "totals": {
            "combinations": len(rows),
            "by_status": counts,
        },
        "combinations": rows,
    }


def _dump(doc: Dict[str, Any]) -> str:
    return json.dumps(doc, indent=2) + "\n"


def write_matrix(doc: Dict[str, Any], path: Path = MATRIX_PATH) -> None:
    path.write_text(_dump(doc))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write; exit non-zero if the on-disk matrix differs "
            "from the regenerated matrix."
        ),
    )
    args = parser.parse_args(argv)

    compat = load_json(COMPAT_PATH)
    builds_doc = load_json(BUILDS_PATH)
    catalog_doc = load_json(CATALOG_PATH)

    doc = generate(compat, builds_doc, catalog_doc)
    rendered = _dump(doc)

    if args.check:
        if not MATRIX_PATH.exists():
            print(
                f"❌ {MATRIX_PATH.relative_to(REPO_ROOT)} does not exist; "
                "run `python3 scripts/generate_firmware_matrix.py`."
            )
            return 1
        on_disk = MATRIX_PATH.read_text()
        if on_disk != rendered:
            print(
                f"❌ {MATRIX_PATH.relative_to(REPO_ROOT)} is stale; "
                "run `python3 scripts/generate_firmware_matrix.py`."
            )
            return 1
        print(
            f"✅ {MATRIX_PATH.relative_to(REPO_ROOT)} is up to date "
            f"({doc['totals']['combinations']} combinations)."
        )
        return 0

    write_matrix(doc)
    print(
        f"✅ Wrote {MATRIX_PATH.relative_to(REPO_ROOT)} "
        f"({doc['totals']['combinations']} combinations)."
    )
    for status, count in sorted(doc["totals"]["by_status"].items()):
        print(f"    {status}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

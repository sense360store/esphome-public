#!/usr/bin/env python3
"""Validate config/webflash-builds.json against config/webflash-compatibility.json.

The compatibility snapshot is the machine-readable mirror of
docs/webflash-contract.md §1–§5 (allowed tokens, forbidden tokens, conflicts,
filename pattern). It is the validator's required source of truth — there is
no hardcoded fallback. If the snapshot is missing or malformed the script
exits non-zero with a pointer back to the contract document.

Usage:
    python3 tests/validate_webflash_builds.py
    python3 tests/validate_webflash_builds.py --builds path/to/builds.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COMPAT = REPO_ROOT / "config" / "webflash-compatibility.json"
DEFAULT_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"

REQUIRED_BUILD_KEYS = [
    "config_string",
    "product_yaml",
    "artifact_name",
    "channel",
    "version",
    "chip_family",
    "hardware_requirements",
    "features",
]

REQUIRED_COMPAT_KEYS = [
    "version",
    "filename_pattern",
    "channels",
    "tokens",
    "forbidden_tokens",
    "mutually_exclusive",
    "conflicts",
    "max_one_of",
]


def load_compat(path: Path) -> dict:
    if not path.exists():
        print(
            f"ERROR: required compatibility snapshot not found: {path}\n"
            "  This file mirrors docs/webflash-contract.md §1–§5 in "
            "machine-readable form and is the validator's source of truth.\n"
            "  Re-create it from the contract document or restore it from git.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: failed to parse {path}: {exc}\n"
            "  This file mirrors docs/webflash-contract.md §1–§5 and must be valid JSON.",
            file=sys.stderr,
        )
        sys.exit(1)


def check_compat_integrity(compat: dict, errors: list) -> None:
    """Validate the compatibility snapshot itself before iterating builds."""
    for key in REQUIRED_COMPAT_KEYS:
        if key not in compat:
            errors.append(f"compatibility snapshot missing required key: {key}")
    if errors:
        return

    tokens = compat.get("tokens", {})
    for slot in ("mounting", "power", "modules"):
        vals = tokens.get(slot)
        if (
            not isinstance(vals, list)
            or not vals
            or not all(isinstance(t, str) for t in vals)
        ):
            errors.append(f"tokens.{slot} must be a non-empty list of strings")

    forbidden = compat.get("forbidden_tokens")
    if not isinstance(forbidden, dict) or not forbidden:
        errors.append("forbidden_tokens must be a non-empty mapping")
    else:
        all_allowed = (
            set(tokens.get("mounting", []))
            | set(tokens.get("power", []))
            | set(tokens.get("modules", []))
        )
        overlap = set(forbidden) & all_allowed
        if overlap:
            errors.append(
                f"forbidden_tokens overlaps allowed tokens: {sorted(overlap)}"
            )

    pattern = compat.get("filename_pattern", "")
    for placeholder in ("{config_string}", "{version}", "{channel}"):
        if placeholder not in pattern:
            errors.append(f"filename_pattern missing placeholder {placeholder}")


def _yaml_contains_config_string(yaml_path: Path, cfg: str) -> bool:
    """True if cfg appears in the YAML or in any file it !include's (one level)."""
    try:
        text = yaml_path.read_text()
    except OSError:
        return False
    if cfg in text:
        return True
    for line in text.splitlines():
        stripped = line.strip()
        if "!include" not in stripped:
            continue
        include_target = stripped.split("!include", 1)[1].strip().strip("\"'")
        if not include_target:
            continue
        include_path = (yaml_path.parent / include_target).resolve()
        try:
            if include_path.exists() and cfg in include_path.read_text():
                return True
        except OSError:
            continue
    return False


def check_build(build: dict, idx: int, compat: dict, errors: list) -> None:
    label = f"build[{idx}]"

    for key in REQUIRED_BUILD_KEYS:
        if key not in build:
            errors.append(f"{label} missing required key: {key}")
            return

    cfg = build["config_string"]
    label = f"build[{idx}] ({cfg})"

    yaml_rel = build["product_yaml"]
    yaml_path = REPO_ROOT / yaml_rel
    if not yaml_path.exists():
        errors.append(f"{label} product_yaml does not exist: {yaml_rel}")

    expected = (
        compat["filename_pattern"]
        .replace("{config_string}", cfg)
        .replace("{version}", build["version"])
        .replace("{channel}", build["channel"])
    )
    if build["artifact_name"] != expected:
        errors.append(
            f"{label} artifact_name does not match filename_pattern.\n"
            f"  expected: {expected}\n"
            f"  actual:   {build['artifact_name']}"
        )

    if build["channel"] not in compat["channels"]:
        errors.append(
            f"{label} channel '{build['channel']}' not in compatibility.channels "
            f"{compat['channels']}"
        )

    tokens_in_cfg = cfg.split("-")
    if len(tokens_in_cfg) < 2:
        errors.append(
            f"{label} config_string must contain at least Mounting-Power"
        )
        return

    mounting = tokens_in_cfg[0]
    power = tokens_in_cfg[1]
    modules = tokens_in_cfg[2:]

    if mounting not in compat["tokens"]["mounting"]:
        errors.append(
            f"{label} mounting token '{mounting}' not in "
            f"{compat['tokens']['mounting']}"
        )
    if power not in compat["tokens"]["power"]:
        errors.append(
            f"{label} power token '{power}' not in {compat['tokens']['power']}"
        )

    forbidden = compat["forbidden_tokens"]
    for tok in tokens_in_cfg:
        if tok in forbidden:
            errors.append(
                f"{label} forbidden token '{tok}' present — use {forbidden[tok]}"
            )

    for tok in modules:
        if tok in forbidden:
            continue
        if tok not in compat["tokens"]["modules"]:
            errors.append(
                f"{label} module token '{tok}' not in allowed modules "
                f"{compat['tokens']['modules']}"
            )

    token_set = set(tokens_in_cfg)
    for pair in compat["mutually_exclusive"]:
        if all(t in token_set for t in pair):
            errors.append(
                f"{label} mutually exclusive tokens both present: {pair}"
            )

    for conflict in compat["conflicts"]:
        if conflict["a"] in token_set and conflict["b"] in token_set:
            errors.append(
                f"{label} conflicting tokens: {conflict['a']} + {conflict['b']} "
                f"({conflict.get('reason', 'no reason given')})"
            )

    for group_name, group_tokens in compat["max_one_of"].items():
        present = [t for t in group_tokens if t in token_set]
        if len(present) > 1:
            errors.append(
                f"{label} more than one '{group_name}' token present: {present}"
            )

    if yaml_path.exists() and not _yaml_contains_config_string(yaml_path, cfg):
        errors.append(
            f"{label} config_string '{cfg}' not found in {yaml_rel} "
            "(or its !include targets) — possible drift between JSON and YAML"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate config/webflash-builds.json against "
            "config/webflash-compatibility.json."
        )
    )
    parser.add_argument("--compat", type=Path, default=DEFAULT_COMPAT)
    parser.add_argument("--builds", type=Path, default=DEFAULT_BUILDS)
    args = parser.parse_args()

    compat = load_compat(args.compat)

    errors: list = []
    check_compat_integrity(compat, errors)
    if errors:
        print("Compatibility snapshot integrity failures:")
        for e in errors:
            print(f"  ❌ {e}")
        return 1

    if not args.builds.exists():
        print(f"ERROR: builds file not found: {args.builds}", file=sys.stderr)
        return 1

    try:
        builds = json.loads(args.builds.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: failed to parse {args.builds}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(builds, list) or not builds:
        print(
            f"ERROR: {args.builds} must be a non-empty JSON array",
            file=sys.stderr,
        )
        return 1

    for idx, build in enumerate(builds):
        if not isinstance(build, dict):
            errors.append(f"build[{idx}] is not a JSON object")
            continue
        check_build(build, idx, compat, errors)

    word = "entry" if len(builds) == 1 else "entries"
    print(f"🔍 Validated {len(builds)} build {word} against {args.compat}")

    if errors:
        print(f"\n❌ {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("✅ All build entries match the compatibility contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

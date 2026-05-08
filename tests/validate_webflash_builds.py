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
"""
Validate the WebFlash firmware build matrix against the local compatibility snapshot.

This script ensures every entry in config/webflash-builds.json is consistent
with the contract mirrored in config/webflash-compatibility.json (which itself
mirrors docs/webflash-contract.md). WebFlash (sense360store/WebFlash) remains
the source of truth for product taxonomy and artifact naming; this validator
catches drift between the WebFlash contract and what this repo declares it
will ship.

Run with:
    python3 tests/validate_webflash_builds.py

Style mirrors tests/validate_configs.py: class-based, instance error/warning
lists, emoji summary output, exit code 1 on any error.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

COMPATIBILITY_PATH = "config/webflash-compatibility.json"
BUILDS_PATH = "config/webflash-builds.json"

REQUIRED_BUILD_FIELDS = [
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
]

GENERIC_FAN_MESSAGE = "Generic Fan token is forbidden; use FanRelay, FanPWM, FanDAC, or FanTRIAC"


class WebflashBuildsValidator:
    """Validates the WebFlash build matrix against the compatibility snapshot."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_json(self, rel_path: str) -> Dict[str, Any]:
        """Load a JSON file under repo_root, recording an error if it fails."""
        full_path = self.repo_root / rel_path
        if not full_path.exists():
            self.errors.append(f"{rel_path}: file does not exist")
            return {}
        try:
            with open(full_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"{rel_path}: JSON parse error - {e}")
            return {}
        except Exception as e:
            self.errors.append(f"{rel_path}: failed to read file - {e}")
            return {}

    def validate_required_fields(self, entry: Dict[str, Any], idx: int) -> bool:
        """Check that every required field is present and non-empty."""
        ok = True
        for field in REQUIRED_BUILD_FIELDS:
            if field not in entry or entry[field] in (None, ""):
                self.errors.append(f"Build entry #{idx}: missing required field '{field}'")
                ok = False
        return ok

    def validate_product_yaml(self, entry: Dict[str, Any]) -> bool:
        """Confirm the referenced product YAML exists on disk."""
        rel = entry.get("product_yaml")
        if not rel:
            return False
        path = self.repo_root / rel
        if not path.is_file():
            self.errors.append(f"product_yaml not found: {rel}")
            return False
        return True

    def validate_config_string(self, config_string: str, compat: Dict[str, Any]) -> bool:
        """Validate config-string grammar against the snapshot's token tables."""
        if config_string == compat.get("rescue_config_string"):
            return True

        tokens = config_string.split("-")
        if len(tokens) < 2:
            self.errors.append(
                f"config_string '{config_string}' must contain at least " f"a mounting and a power token"
            )
            return False

        ok = True
        forbidden = set(compat.get("forbidden_tokens", []))
        mounting = set(compat.get("mounting_tokens", []))
        power = set(compat.get("power_tokens", []))
        modules = set(compat.get("module_tokens", []))

        # Forbidden / legacy tokens anywhere
        for token in tokens:
            if token in forbidden:
                if token == "Fan":
                    self.errors.append(f"{GENERIC_FAN_MESSAGE} (in '{config_string}')")
                else:
                    self.errors.append(
                        f"Forbidden legacy token '{token}' in " f"'{config_string}'; see docs/webflash-contract.md §3"
                    )
                ok = False

        # Mounting (first token)
        if tokens[0] not in mounting:
            self.errors.append(
                f"Invalid mounting token '{tokens[0]}' in '{config_string}'; " f"allowed: {sorted(mounting)}"
            )
            ok = False

        # Power (second token)
        if tokens[1] not in power:
            self.errors.append(f"Invalid power token '{tokens[1]}' in '{config_string}'; " f"allowed: {sorted(power)}")
            ok = False

        # Module tokens (remaining)
        for token in tokens[2:]:
            if token in forbidden:
                continue
            if token not in modules:
                self.errors.append(f"Unknown module token '{token}' in '{config_string}'")
                ok = False

        # Mutually exclusive groups
        for group in compat.get("mutually_exclusive_groups", []):
            present = [t for t in group if t in tokens]
            if len(present) > 1:
                self.errors.append(f"{' and '.join(group)} are mutually exclusive in " f"'{config_string}'")
                ok = False

        # Conflicting pairs
        for pair in compat.get("conflicting_pairs", []):
            if all(t in tokens for t in pair):
                a, b = pair[0], pair[1]
                self.errors.append(f"{a} conflicts with {b} in '{config_string}'; " f"see docs/webflash-contract.md §5")
                ok = False

        return ok

    def validate_artifact_name(self, entry: Dict[str, Any], compat: Dict[str, Any]) -> bool:
        """Confirm artifact_name matches the canonical template."""
        template = compat.get(
            "artifact_name_template",
            "Sense360-{config_string}-v{version}-{channel}.bin",
        )
        try:
            expected = template.format(
                config_string=entry["config_string"],
                version=entry["version"],
                channel=entry["channel"],
            )
        except KeyError:
            return False
        actual = entry.get("artifact_name")
        if actual != expected:
            self.errors.append(f"artifact_name mismatch: expected {expected}, got {actual}")
            return False
        return True

    def validate_channel(self, entry: Dict[str, Any], compat: Dict[str, Any]) -> bool:
        """Confirm channel is in the snapshot's allowed_channels list."""
        allowed = compat.get("allowed_channels", [])
        channel = entry.get("channel")
        if channel not in allowed:
            self.errors.append(f"channel '{channel}' is not in allowed_channels {allowed}")
            return False
        return True

    def validate_release_one(self, builds: List[Dict[str, Any]], compat: Dict[str, Any]) -> bool:
        """Confirm the Release-One required config is present with the canonical artifact."""
        required = compat.get("release_one_required_config")
        if not required:
            return True

        expected_artifact = f"Sense360-{required}-v1.0.0-stable.bin"
        for entry in builds:
            if entry.get("config_string") == required:
                if entry.get("artifact_name") != expected_artifact:
                    self.errors.append(
                        f"Release-One artifact_name mismatch: expected "
                        f"{expected_artifact}, got {entry.get('artifact_name')}"
                    )
                    return False
                return True

        self.errors.append(f"Release-One config '{required}' not present in {BUILDS_PATH}")
        return False

    def validate_all(self) -> Tuple[int, int]:
        """Run the full validation pipeline. Returns (total_entries, failed_entries)."""
        compat = self.load_json(COMPATIBILITY_PATH)
        builds_doc = self.load_json(BUILDS_PATH)
        if not compat or not builds_doc:
            return 0, 0

        builds = builds_doc.get("builds")
        if not isinstance(builds, list):
            self.errors.append(f"{BUILDS_PATH}: top-level 'builds' must be a list")
            return 0, 0

        total = len(builds)
        failed = 0
        for idx, entry in enumerate(builds, start=1):
            if not isinstance(entry, dict):
                self.errors.append(f"Build entry #{idx}: must be a JSON object")
                failed += 1
                continue

            entry_ok = True

            if not self.validate_required_fields(entry, idx):
                failed += 1
                continue

            if not self.validate_product_yaml(entry):
                entry_ok = False

            if not self.validate_config_string(entry["config_string"], compat):
                entry_ok = False

            if not self.validate_artifact_name(entry, compat):
                entry_ok = False

            if not self.validate_channel(entry, compat):
                entry_ok = False

            if not entry_ok:
                failed += 1

        # Matrix-level check: Release-One must be present.
        self.validate_release_one(builds, compat)

        return total, failed

    def print_summary(self, total: int, failed: int):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print(f"WebFlash Build Matrix: {total} build(s) checked, {failed} failed")
        print("=" * 70)

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ❌ {error}")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All WebFlash build entries are valid!")


def main():
    """Main validation entry point."""
    repo_root = Path(__file__).parent.parent
    validator = WebflashBuildsValidator(repo_root)

    print("🔍 Validating WebFlash build matrix...\n")
    total, failed = validator.validate_all()
    validator.print_summary(total, failed)

    sys.exit(1 if failed > 0 or len(validator.errors) > 0 else 0)


if __name__ == "__main__":
    main()

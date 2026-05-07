#!/usr/bin/env python3
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

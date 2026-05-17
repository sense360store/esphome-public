#!/usr/bin/env python3
"""Validate config/webflash-builds.json against config/webflash-compatibility.json.

The compatibility snapshot is the machine-readable mirror of
docs/webflash-contract.md. WebFlash (sense360store/WebFlash) remains the source
of truth for product taxonomy and artifact naming; this validator catches
drift between the WebFlash contract and what this repo declares it will ship.

Run with:
    python3 tests/validate_webflash_builds.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
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

GENERIC_FAN_MESSAGE = (
    "Generic Fan token is forbidden; use FanRelay, FanPWM, FanDAC, or FanTRIAC"
)

FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")


class WebflashBuildsValidator:
    """Validates the WebFlash build matrix against the compatibility snapshot."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _load_json(self, rel_path: str) -> Any:
        full_path = self.repo_root / rel_path
        if not full_path.exists():
            self.errors.append(f"{rel_path}: file does not exist")
            return None
        try:
            return json.loads(full_path.read_text())
        except json.JSONDecodeError as e:
            self.errors.append(f"{rel_path}: JSON parse error - {e}")
            return None

    def _validate_required_fields(self, entry: Dict[str, Any], idx: int) -> bool:
        ok = True
        for field in REQUIRED_BUILD_FIELDS:
            if field not in entry or entry[field] in (None, ""):
                self.errors.append(
                    f"Build entry #{idx}: missing required field '{field}'"
                )
                ok = False
        return ok

    def _validate_product_yaml(self, entry: Dict[str, Any]) -> bool:
        rel = entry.get("product_yaml", "")
        path = self.repo_root / rel
        if not path.is_file():
            self.errors.append(f"product_yaml not found: {rel}")
            return False
        return True

    def _validate_config_string(
        self, config_string: str, compat: Dict[str, Any]
    ) -> bool:
        if config_string == compat.get("rescue_config_string"):
            return True

        tokens = config_string.split("-")
        if len(tokens) < 2:
            self.errors.append(
                f"config_string '{config_string}' must contain at least "
                "a mounting and a power token"
            )
            return False

        ok = True
        forbidden = set(compat.get("forbidden_tokens", []))
        mounting = set(compat.get("canonical_mounting", []))
        power = set(compat.get("canonical_power", []))
        modules = set(compat.get("canonical_modules", []))

        for token in tokens:
            if token in forbidden:
                if token == "Fan":
                    self.errors.append(f"{GENERIC_FAN_MESSAGE} (in '{config_string}')")
                else:
                    self.errors.append(
                        f"Forbidden legacy token '{token}' in "
                        f"'{config_string}'; see docs/webflash-contract.md"
                    )
                ok = False

        if tokens[0] not in mounting:
            self.errors.append(
                f"Invalid mounting token '{tokens[0]}' in "
                f"'{config_string}'; allowed: {sorted(mounting)}"
            )
            ok = False

        if tokens[1] not in power:
            self.errors.append(
                f"Invalid power token '{tokens[1]}' in "
                f"'{config_string}'; allowed: {sorted(power)}"
            )
            ok = False

        for token in tokens[2:]:
            if token in forbidden:
                continue
            if token not in modules:
                self.errors.append(
                    f"Unknown module token '{token}' in '{config_string}'"
                )
                ok = False

        rules = compat.get("rules", {})

        if (
            rules.get("airiq_and_ventiq_mutually_exclusive")
            and "AirIQ" in tokens
            and "VentIQ" in tokens
        ):
            self.errors.append(
                f"AirIQ and VentIQ are mutually exclusive in '{config_string}'"
            )
            ok = False

        if (
            rules.get("fandac_conflicts_with_airiq")
            and "FanDAC" in tokens
            and "AirIQ" in tokens
        ):
            self.errors.append(
                f"FanDAC conflicts with AirIQ in '{config_string}'; "
                "see docs/webflash-contract.md"
            )
            ok = False

        present_fans = [t for t in FAN_DRIVER_TOKENS if t in tokens]
        if len(present_fans) > 1:
            self.errors.append(
                f"more than one fan-driver token in '{config_string}': "
                f"{present_fans}"
            )
            ok = False

        return ok

    def _validate_artifact_name(
        self, entry: Dict[str, Any], compat: Dict[str, Any]
    ) -> bool:
        pattern = compat.get(
            "artifact_pattern",
            "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin",
        )
        expected = (
            pattern.replace("{CONFIG_STRING}", entry["config_string"])
            .replace("{VERSION}", entry["version"])
            .replace("{CHANNEL}", entry["channel"])
        )
        actual = entry.get("artifact_name")
        if actual != expected:
            self.errors.append(
                f"artifact_name mismatch: expected {expected}, got {actual}"
            )
            return False
        return True

    def _validate_channel(self, entry: Dict[str, Any], compat: Dict[str, Any]) -> bool:
        allowed = compat.get("allowed_channels", [])
        channel = entry.get("channel")
        if channel not in allowed:
            self.errors.append(
                f"channel '{channel}' is not in allowed_channels {allowed}"
            )
            return False
        return True

    def _validate_release_one(
        self,
        builds: List[Dict[str, Any]],
        compat: Dict[str, Any],
    ) -> None:
        required = compat.get("release_one_required_configs", [])
        present = {b.get("config_string") for b in builds if isinstance(b, dict)}
        for cs in required:
            if cs not in present:
                self.errors.append(
                    f"Release-One config '{cs}' not present in {BUILDS_PATH}"
                )

    def validate_all(self) -> Tuple[int, int]:
        compat = self._load_json(COMPATIBILITY_PATH)
        builds_doc = self._load_json(BUILDS_PATH)
        if compat is None or builds_doc is None:
            return 0, 0

        if not isinstance(builds_doc, dict):
            self.errors.append(f"{BUILDS_PATH}: top-level must be a JSON object")
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

            if not self._validate_required_fields(entry, idx):
                failed += 1
                continue

            entry_ok = True
            if not self._validate_product_yaml(entry):
                entry_ok = False
            if not self._validate_config_string(entry["config_string"], compat):
                entry_ok = False
            if not self._validate_artifact_name(entry, compat):
                entry_ok = False
            if not self._validate_channel(entry, compat):
                entry_ok = False

            if not entry_ok:
                failed += 1

        self._validate_release_one(builds, compat)

        return total, failed

    def print_summary(self, total: int, failed: int) -> None:
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


def main() -> int:
    validator = WebflashBuildsValidator(REPO_ROOT)
    print("🔍 Validating WebFlash build matrix...\n")
    total, failed = validator.validate_all()
    validator.print_summary(total, failed)
    return 1 if failed > 0 or validator.errors else 0


if __name__ == "__main__":
    sys.exit(main())

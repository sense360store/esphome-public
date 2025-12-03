#!/usr/bin/env python3
"""
Validate ESPHome configuration files for Sense360 devices.
This script checks YAML syntax, structure, and common configuration issues.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple


# Custom YAML constructors for ESPHome tags
def esphome_constructor(loader, node):
    """Handle ESPHome custom tags like !secret, !include, !extend, !lambda, etc."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Register ESPHome custom tags
yaml.add_constructor("!secret", esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_constructor("!include", esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_constructor("!extend", esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_constructor("!lambda", esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_constructor("!remove", esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", esphome_constructor, Loader=yaml.SafeLoader)


class ConfigValidator:
    """Validates ESPHome configuration files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_yaml_syntax(self, file_path: Path) -> bool:
        """Check if YAML file has valid syntax."""
        try:
            with open(file_path, "r") as f:
                yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"{file_path}: YAML syntax error - {e}")
            return False
        except Exception as e:
            self.errors.append(f"{file_path}: Failed to read file - {e}")
            return False

    def validate_product_config(self, file_path: Path) -> bool:
        """Validate product configuration structure."""
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            if not config:
                self.errors.append(f"{file_path}: Empty configuration file")
                return False

            # Check if this uses packages pattern (package-based composition)
            uses_packages = "packages" in config and isinstance(config.get("packages"), dict)

            # For package-based configs, esphome section may be in a package
            if not uses_packages:
                # Check for required top-level keys for standalone configs
                required_keys = ["substitutions", "esphome"]
                for key in required_keys:
                    if key not in config:
                        self.errors.append(
                            f"{file_path}: Missing required key '{key}'"
                        )
                        return False

            # Validate substitutions if present
            if "substitutions" in config:
                subs = config["substitutions"]
                if not isinstance(subs, dict):
                    self.errors.append(
                        f"{file_path}: 'substitutions' must be a dictionary"
                    )
                    return False

                # Only warn about missing device_name/friendly_name for non-package configs
                # or for configs that look like they should be customer-facing
                if not uses_packages and "products" in str(file_path):
                    recommended_subs = ["device_name", "friendly_name"]
                    for sub in recommended_subs:
                        if sub not in subs:
                            self.warnings.append(
                                f"{file_path}: Missing recommended substitution '{sub}'"
                            )

            # Validate esphome section if present
            if "esphome" in config:
                esphome = config["esphome"]
                if not isinstance(esphome, dict):
                    self.errors.append(
                        f"{file_path}: 'esphome' must be a dictionary"
                    )
                    return False

                if "name" not in esphome:
                    self.warnings.append(
                        f"{file_path}: 'esphome.name' should be specified"
                    )

            return True

        except Exception as e:
            self.errors.append(f"{file_path}: Validation error - {e}")
            return False

    def validate_package_references(self, file_path: Path) -> bool:
        """Check if package references are valid."""
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            if not config or "packages" not in config:
                return True

            packages = config["packages"]
            if not isinstance(packages, dict):
                return True

            for pkg_name, pkg_config in packages.items():
                if isinstance(pkg_config, dict) and "!include" in str(pkg_config):
                    # Check if included file exists
                    include_path = self.resolve_include_path(file_path, pkg_config)
                    if include_path and not include_path.exists():
                        self.errors.append(
                            f"{file_path}: Package '{pkg_name}' references non-existent file {include_path}"
                        )
                        return False

            return True

        except Exception as e:
            self.warnings.append(
                f"{file_path}: Could not validate package references - {e}"
            )
            return True

    def resolve_include_path(self, base_file: Path, config: Any) -> Path:
        """Resolve include path relative to base file."""
        # This is a simplified version - ESPHome's actual include resolution is more complex
        if isinstance(config, str) and config.startswith("!include"):
            include_file = config.replace("!include", "").strip()
            return base_file.parent / include_file
        return None

    def validate_all_configs(self) -> Tuple[int, int]:
        """Validate all configuration files in the repository."""
        config_dirs = ["products", "packages", "base", "features", "hardware", "tests"]
        total_files = 0
        failed_files = 0

        for config_dir in config_dirs:
            dir_path = self.repo_root / config_dir
            if not dir_path.exists():
                continue

            yaml_files = list(dir_path.rglob("*.yaml")) + list(
                dir_path.rglob("*.yml")
            )

            for yaml_file in yaml_files:
                total_files += 1
                print(f"Validating: {yaml_file.relative_to(self.repo_root)}")

                # Basic YAML syntax check
                if not self.validate_yaml_syntax(yaml_file):
                    failed_files += 1
                    continue

                # Product-specific validation
                if "products" in str(yaml_file):
                    if not self.validate_product_config(yaml_file):
                        failed_files += 1
                        continue

                # Package reference validation
                if not self.validate_package_references(yaml_file):
                    failed_files += 1
                    continue

        return total_files, failed_files

    def print_summary(self, total: int, failed: int):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print(f"Validation Summary: {total} files checked, {failed} failed")
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
            print("\n✅ All configuration files are valid!")


def main():
    """Main validation entry point."""
    repo_root = Path(__file__).parent.parent
    validator = ConfigValidator(repo_root)

    print("🔍 Validating ESPHome configurations...\n")
    total, failed = validator.validate_all_configs()
    validator.print_summary(total, failed)

    # Exit with error code if validation failed
    sys.exit(1 if failed > 0 or len(validator.errors) > 0 else 0)


if __name__ == "__main__":
    main()

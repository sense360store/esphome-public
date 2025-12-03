#!/usr/bin/env python3
"""
Batch validation script for ESPHome configs.
Validates ALL product configs and collects ALL errors at once.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class ESPHomeBatchValidator:
    """Validates all ESPHome configurations and collects errors."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.validation_results: Dict[str, Tuple[bool, str]] = {}

    def create_secrets_file(self):
        """Create a secrets.yaml file for testing."""
        secrets_content = """wifi_ssid: "TestNetwork"
wifi_password: "TestPassword123"
api_encryption_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="
ota_password: "test-ota-password"
fallback_ap_password: "fallback123"
web_username: "admin"
web_password: "test_web_password"
"""
        secrets_path = self.repo_root / "secrets.yaml"
        secrets_path.write_text(secrets_content)

        # Also create in products directory
        products_secrets = self.repo_root / "products" / "secrets.yaml"
        products_secrets.write_text(secrets_content)

        print(f"✅ Created secrets.yaml for testing")

    def validate_config(self, config_file: Path) -> Tuple[bool, str]:
        """Validate a single ESPHome config and return status and output."""
        try:
            result = subprocess.run(
                ["esphome", "config", str(config_file)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            # ESPHome returns non-zero exit code on validation failure
            success = result.returncode == 0
            output = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Validation timed out after 60 seconds"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def validate_all_products(self) -> Dict[str, Tuple[bool, str]]:
        """Validate all product configurations."""
        products_dir = self.repo_root / "products"
        yaml_files = sorted(products_dir.glob("*.yaml"))

        print(f"\n🔍 Found {len(yaml_files)} product configurations to validate\n")

        for yaml_file in yaml_files:
            relative_path = yaml_file.relative_to(self.repo_root)
            print(f"Validating: {relative_path}... ", end="", flush=True)

            success, output = self.validate_config(yaml_file)
            self.validation_results[str(relative_path)] = (success, output)

            if success:
                print("✅")
            else:
                print("❌")

        return self.validation_results

    def print_summary(self):
        """Print detailed summary of all validation results."""
        total = len(self.validation_results)
        passed = sum(1 for success, _ in self.validation_results.values() if success)
        failed = total - passed

        print("\n" + "=" * 80)
        print(f"VALIDATION SUMMARY: {passed}/{total} passed, {failed}/{total} failed")
        print("=" * 80)

        if failed == 0:
            print("\n✅ All configurations are valid!")
            return

        print("\n❌ FAILED CONFIGURATIONS:\n")

        for config_path, (success, output) in self.validation_results.items():
            if not success:
                print(f"\n{'=' * 80}")
                print(f"File: {config_path}")
                print(f"{'=' * 80}")

                # Extract and display errors
                self._print_errors(output)

    def _print_errors(self, output: str):
        """Extract and print errors from ESPHome output."""
        lines = output.split('\n')
        in_error_section = False
        error_lines = []

        for line in lines:
            # Look for error indicators
            if any(keyword in line.lower() for keyword in ['failed config', 'error:', 'duplicate']):
                in_error_section = True

            if in_error_section:
                error_lines.append(line)

                # Stop at certain markers
                if line.strip().startswith('===') or line.strip().startswith('---'):
                    break

        # If we found specific errors, print them
        if error_lines:
            for line in error_lines:
                if line.strip():
                    print(f"  {line}")
        else:
            # Otherwise print last 30 lines which usually contain the error
            print("  Last 30 lines of output:")
            for line in lines[-30:]:
                if line.strip():
                    print(f"  {line}")

    def cleanup(self):
        """Remove temporary secrets files."""
        for secrets_path in [
            self.repo_root / "secrets.yaml",
            self.repo_root / "products" / "secrets.yaml"
        ]:
            if secrets_path.exists():
                secrets_path.unlink()


def check_esphome_installed() -> bool:
    """Check if ESPHome is installed."""
    try:
        subprocess.run(
            ["esphome", "version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main validation entry point."""
    print("🔍 ESPHome Batch Validation Tool\n")

    # Check if ESPHome is installed
    if not check_esphome_installed():
        print("❌ ESPHome is not installed!")
        print("\nTo install ESPHome, run:")
        print("  pip install esphome")
        sys.exit(1)

    # Get ESPHome version
    result = subprocess.run(
        ["esphome", "version"],
        capture_output=True,
        text=True
    )
    print(f"ESPHome version: {result.stdout.strip()}\n")

    # Run validation
    repo_root = Path(__file__).parent.parent
    validator = ESPHomeBatchValidator(repo_root)

    try:
        validator.create_secrets_file()
        validator.validate_all_products()
        validator.print_summary()

        # Return error code if any validation failed
        failed = sum(1 for success, _ in validator.validation_results.values() if not success)
        sys.exit(1 if failed > 0 else 0)

    finally:
        validator.cleanup()


if __name__ == "__main__":
    main()

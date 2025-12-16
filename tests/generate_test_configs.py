#!/usr/bin/env python3
"""
Generate ESPHome test configurations for all valid Sense360 module combinations.

This script implements the complete valid ruleset for Sense360 device configurations:

CORE (pick one):
- Ceiling: CORE-C, CORE-V-C (Voice)
- Wall/Desk: CORE-W, CORE-V-W (Voice)

POWER (pick one):
- USB, POE, PWR (240V)

LIGHTING:
- Core Voice: LED+MIC required (matched to form factor)
- Core: LED optional

MODULE RULES:
- Ceiling: AirIQ-C, Bathroom-C (mutually exclusive), Comfort-C, Presence-C, Fan
- Wall: AirIQ-W, Comfort-W, Presence-W, Fan (no Bathroom)

Constraints:
- AirIQ-C and Bathroom-C cannot be used together
- Wall has no Bathroom option
"""

import os
import sys
import itertools
import argparse
import tempfile
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum


class FormFactor(Enum):
    CEILING = "ceiling"
    WALL = "wall"


class CoreType(Enum):
    CORE_C = ("sense360_core_ceiling", FormFactor.CEILING, False)
    CORE_V_C = ("sense360_core_voice_ceiling", FormFactor.CEILING, True)
    CORE_W = ("sense360_core_wall", FormFactor.WALL, False)
    CORE_V_W = ("sense360_core_voice_wall", FormFactor.WALL, True)

    def __init__(self, package_name: str, form_factor: FormFactor, has_voice: bool):
        self.package_name = package_name
        self.form_factor = form_factor
        self.has_voice = has_voice


class PowerType(Enum):
    USB = "power_usb"
    POE = "power_poe"
    PWR = "power_240v"


class LEDType(Enum):
    NONE = None
    LED_CEILING = "led_ring_ceiling"
    LED_WALL = "led_ring_wall"
    LED_MIC_CEILING = "led_ring_mic_ceiling"
    LED_MIC_WALL = "led_ring_mic_wall"


class ModuleType(Enum):
    # Ceiling modules
    AIRIQ_C = ("airiq_ceiling", FormFactor.CEILING, "airiq")
    BATHROOM_C = ("airiq_bathroom_base", FormFactor.CEILING, "bathroom")
    COMFORT_C = ("comfort_ceiling", FormFactor.CEILING, "comfort")
    PRESENCE_C = ("presence_ceiling", FormFactor.CEILING, "presence")
    FAN_PWM = ("fan_pwm", None, "fan_pwm")  # Works with both form factors
    FAN_GP8403 = ("fan_gp8403", None, "fan_gp8403")

    # Wall modules
    AIRIQ_W = ("airiq_wall", FormFactor.WALL, "airiq")
    COMFORT_W = ("comfort_wall", FormFactor.WALL, "comfort")
    PRESENCE_W = ("presence_wall", FormFactor.WALL, "presence")

    def __init__(self, package_name: str, form_factor: Optional[FormFactor], category: str):
        self.package_name = package_name
        self.form_factor = form_factor
        self.category = category


@dataclass
class TestConfig:
    """Represents a single test configuration."""
    name: str
    core: CoreType
    power: PowerType
    led: LEDType
    modules: List[ModuleType] = field(default_factory=list)

    def get_config_name(self) -> str:
        """Generate a descriptive config name."""
        parts = [self.core.name.lower().replace("_", "-")]
        parts.append(self.power.name.lower())
        if self.led != LEDType.NONE:
            parts.append("led" if "MIC" not in self.led.name else "ledmic")
        for mod in sorted(self.modules, key=lambda m: m.category):
            parts.append(mod.category.replace("_", ""))
        return "-".join(parts)

    def generate_yaml(self) -> str:
        """Generate the ESPHome YAML configuration."""
        lines = [
            "---",
            f"# Auto-generated test config: {self.get_config_name()}",
            f"# Core: {self.core.name}, Power: {self.power.name}, LED: {self.led.name}",
            f"# Modules: {', '.join(m.name for m in self.modules) or 'None'}",
            "",
            "substitutions:",
            f'  device_name: test-{self.get_config_name()[:20]}',
            f'  friendly_name: "Test {self.get_config_name()[:30]}"',
            '  timezone: "America/New_York"',
            '  api_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="',
            '  ota_password: "test-ota-password"',
        ]

        # Add module-specific substitutions
        # Check if fan_pwm module is present
        has_fan_pwm = any(mod.category == "fan_pwm" for mod in self.modules)
        if has_fan_pwm:
            lines.extend([
                '  fan_pwm_pin: "${expansion_gpio1}"  # GPIO5',
                '  fan_tach_pin: "${expansion_gpio2}"  # GPIO6',
            ])

        # Check if fan_gp8403 module is present - ceiling uses different I2C bus name
        has_fan_gp8403 = any(mod.category == "fan_gp8403" for mod in self.modules)
        if has_fan_gp8403 and self.core.form_factor == FormFactor.CEILING:
            lines.extend([
                '  fan_dac_i2c_id: expansion_i2c  # Ceiling uses expansion_i2c instead of i2c0',
            ])

        # Check if presence module is included (requires ld2450 external component)
        has_presence = any(mod.category == "presence" for mod in self.modules)

        lines.extend([
            "",
            "packages:",
        ])

        # Add external_components if presence module is used (requires ld2450)
        if has_presence:
            lines.extend([
                "  # External components (ld2450 radar)",
                "  external_components: !include ../../packages/base/external_components.yaml",
                "",
            ])

        lines.extend([
            "  # Base system components",
            "  base_wifi: !include ../../packages/base/wifi.yaml",
            "  base_logging: !include ../../packages/base/logging.yaml",
            "  base_api: !include ../../packages/base/api_encrypted.yaml",
            "  base_ota: !include ../../packages/base/ota.yaml",
            "  base_time: !include ../../packages/base/time.yaml",
            "",
            "  # Core hardware",
            f"  core_hardware: !include ../../packages/hardware/{self.core.package_name}.yaml",
            "",
            "  # Power module",
            f"  power_module: !include ../../packages/hardware/{self.power.value}.yaml",
        ])

        # Add LED package if present
        if self.led != LEDType.NONE:
            lines.extend([
                "",
                "  # LED module",
                f"  led_module: !include ../../packages/hardware/{self.led.value}.yaml",
            ])

        # Add expansion modules
        if self.modules:
            lines.extend(["", "  # Expansion modules"])
            for i, mod in enumerate(self.modules):
                lines.append(f"  module_{mod.category}: !include ../../packages/expansions/{mod.package_name}.yaml")

        lines.append("")
        return "\n".join(lines)


class ConfigGenerator:
    """Generates all valid test configurations."""

    # GitHub Actions matrix limit
    MAX_MATRIX_SIZE = 256

    # Ceiling module combinations (from user's spec)
    CEILING_MODULE_SETS: List[Set[str]] = [
        # Empty (no modules)
        set(),
        # Single modules
        {"comfort"}, {"presence"}, {"fan_pwm"}, {"fan_gp8403"}, {"airiq"}, {"bathroom"},
        # Two-module builds
        {"comfort", "presence"}, {"comfort", "fan_pwm"}, {"comfort", "fan_gp8403"},
        {"presence", "fan_pwm"}, {"presence", "fan_gp8403"},
        {"airiq", "comfort"}, {"airiq", "presence"}, {"airiq", "fan_pwm"}, {"airiq", "fan_gp8403"},
        {"bathroom", "comfort"}, {"bathroom", "presence"}, {"bathroom", "fan_pwm"}, {"bathroom", "fan_gp8403"},
        # Three-module builds
        {"comfort", "presence", "fan_pwm"}, {"comfort", "presence", "fan_gp8403"},
        {"airiq", "comfort", "presence"}, {"airiq", "comfort", "fan_pwm"}, {"airiq", "comfort", "fan_gp8403"},
        {"airiq", "presence", "fan_pwm"}, {"airiq", "presence", "fan_gp8403"},
        {"bathroom", "comfort", "presence"}, {"bathroom", "comfort", "fan_pwm"}, {"bathroom", "comfort", "fan_gp8403"},
        {"bathroom", "presence", "fan_pwm"}, {"bathroom", "presence", "fan_gp8403"},
        # Four-module builds
        {"airiq", "comfort", "presence", "fan_pwm"}, {"airiq", "comfort", "presence", "fan_gp8403"},
        {"bathroom", "comfort", "presence", "fan_pwm"}, {"bathroom", "comfort", "presence", "fan_gp8403"},
    ]

    # Wall module combinations (no bathroom)
    WALL_MODULE_SETS: List[Set[str]] = [
        # Empty
        set(),
        # Single modules
        {"comfort"}, {"presence"}, {"fan_pwm"}, {"fan_gp8403"}, {"airiq"},
        # Two-module builds
        {"comfort", "presence"}, {"comfort", "fan_pwm"}, {"comfort", "fan_gp8403"},
        {"presence", "fan_pwm"}, {"presence", "fan_gp8403"},
        {"airiq", "comfort"}, {"airiq", "presence"}, {"airiq", "fan_pwm"}, {"airiq", "fan_gp8403"},
        # Three-module builds
        {"comfort", "presence", "fan_pwm"}, {"comfort", "presence", "fan_gp8403"},
        {"airiq", "comfort", "presence"}, {"airiq", "comfort", "fan_pwm"}, {"airiq", "comfort", "fan_gp8403"},
        {"airiq", "presence", "fan_pwm"}, {"airiq", "presence", "fan_gp8403"},
        # Four-module builds
        {"airiq", "comfort", "presence", "fan_pwm"}, {"airiq", "comfort", "presence", "fan_gp8403"},
    ]

    # Map category to module type for each form factor
    CEILING_MODULES = {
        "airiq": ModuleType.AIRIQ_C,
        "bathroom": ModuleType.BATHROOM_C,
        "comfort": ModuleType.COMFORT_C,
        "presence": ModuleType.PRESENCE_C,
        "fan_pwm": ModuleType.FAN_PWM,
        "fan_gp8403": ModuleType.FAN_GP8403,
    }

    WALL_MODULES = {
        "airiq": ModuleType.AIRIQ_W,
        "comfort": ModuleType.COMFORT_W,
        "presence": ModuleType.PRESENCE_W,
        "fan_pwm": ModuleType.FAN_PWM,
        "fan_gp8403": ModuleType.FAN_GP8403,
    }

    def __init__(self, include_all_power: bool = False, include_all_led: bool = False):
        """
        Initialize the config generator.

        Args:
            include_all_power: If True, generate configs for all power types.
                              If False, only use USB for reduced test count.
            include_all_led: If True, generate configs with/without LED for non-voice.
                            If False, include LED for all (voice requires it anyway).
        """
        self.include_all_power = include_all_power
        self.include_all_led = include_all_led

    def get_led_options(self, core: CoreType) -> List[LEDType]:
        """Get valid LED options for a core type."""
        if core.has_voice:
            # Voice cores require LED+MIC
            if core.form_factor == FormFactor.CEILING:
                return [LEDType.LED_MIC_CEILING]
            else:
                return [LEDType.LED_MIC_WALL]
        else:
            # Non-voice cores: LED optional
            if core.form_factor == FormFactor.CEILING:
                if self.include_all_led:
                    return [LEDType.NONE, LEDType.LED_CEILING]
                return [LEDType.LED_CEILING]  # Default to having LED
            else:
                if self.include_all_led:
                    return [LEDType.NONE, LEDType.LED_WALL]
                return [LEDType.LED_WALL]  # Default to having LED

    def get_power_options(self) -> List[PowerType]:
        """Get power type options based on config."""
        if self.include_all_power:
            return list(PowerType)
        return [PowerType.USB]  # Default to just USB for quick testing

    def get_module_sets(self, form_factor: FormFactor) -> List[Set[str]]:
        """Get valid module sets for a form factor."""
        if form_factor == FormFactor.CEILING:
            return self.CEILING_MODULE_SETS
        return self.WALL_MODULE_SETS

    def get_module_map(self, form_factor: FormFactor) -> dict:
        """Get module category to type mapping for a form factor."""
        if form_factor == FormFactor.CEILING:
            return self.CEILING_MODULES
        return self.WALL_MODULES

    def get_default_led(self, core: CoreType) -> LEDType:
        """Get the default (non-NONE) LED type for a core."""
        if core.has_voice:
            if core.form_factor == FormFactor.CEILING:
                return LEDType.LED_MIC_CEILING
            else:
                return LEDType.LED_MIC_WALL
        else:
            if core.form_factor == FormFactor.CEILING:
                return LEDType.LED_CEILING
            else:
                return LEDType.LED_WALL

    def generate_all_configs(self) -> List[TestConfig]:
        """
        Generate comprehensive test configurations within GitHub Actions limits.

        Strategy to stay under 256 config limit:
        1. Test ALL module combinations with USB power (covers module permutations)
        2. Test ALL power types with representative module subsets (covers power variations)

        This provides comprehensive coverage without the combinatorial explosion of
        testing every module combination with every power type.
        """
        configs = []
        seen_names = set()

        def add_config(config: TestConfig):
            """Add config if not already present (dedup by name)."""
            name = config.get_config_name()
            if name not in seen_names:
                seen_names.add(name)
                configs.append(config)

        # Part 1: Test ALL module combinations with USB power only
        # This covers all module permutations for each core type
        for core in CoreType:
            led = self.get_default_led(core)  # Always use actual LED for base tests
            module_sets = self.get_module_sets(core.form_factor)
            module_map = self.get_module_map(core.form_factor)

            for module_set in module_sets:
                modules = [module_map[cat] for cat in module_set]
                add_config(TestConfig(
                    name=f"{core.name}-USB-{led.name}",
                    core=core,
                    power=PowerType.USB,
                    led=led,
                    modules=modules,
                ))

        # Part 2: Test ALL power types with representative module configurations
        # This ensures power module compatibility is tested
        representative_module_sets = [
            set(),  # No modules
            {"comfort", "presence"},  # Common combo
            {"airiq", "comfort", "presence", "fan_pwm"},  # Full load
        ]

        for core in CoreType:
            led = self.get_default_led(core)  # Always use actual LED for base tests
            module_map = self.get_module_map(core.form_factor)

            for power in PowerType:
                for module_set in representative_module_sets:
                    # Filter to valid modules for this form factor
                    valid_modules = {m for m in module_set if m in module_map}
                    modules = [module_map[cat] for cat in valid_modules]
                    add_config(TestConfig(
                        name=f"{core.name}-{power.name}-{led.name}",
                        core=core,
                        power=power,
                        led=led,
                        modules=modules,
                    ))

        # Part 3: Test LED variations for non-voice cores (if include_all_led)
        if self.include_all_led:
            for core in CoreType:
                if not core.has_voice:  # Voice cores have fixed LED
                    module_map = self.get_module_map(core.form_factor)
                    # Test no-LED with a few module configs
                    for module_set in [set(), {"presence"}]:
                        valid_modules = {m for m in module_set if m in module_map}
                        modules = [module_map[cat] for cat in valid_modules]
                        add_config(TestConfig(
                            name=f"{core.name}-USB-NONE",
                            core=core,
                            power=PowerType.USB,
                            led=LEDType.NONE,
                            modules=modules,
                        ))

        # Validate we're under the GitHub Actions limit
        if len(configs) > self.MAX_MATRIX_SIZE:
            print(f"WARNING: Generated {len(configs)} configs, exceeds limit of {self.MAX_MATRIX_SIZE}",
                  file=sys.stderr)
            # Truncate to stay within limits (shouldn't happen with current logic)
            configs = configs[:self.MAX_MATRIX_SIZE]

        return configs

    def generate_representative_configs(self) -> List[TestConfig]:
        """Generate a representative subset of configs for quick CI testing."""
        configs = []

        # Test each core type with USB power and LED
        for core in CoreType:
            led = self.get_led_options(core)[0]  # Required LED for voice, default for non-voice

            # 1. Minimal config (no modules)
            configs.append(TestConfig(
                name=f"{core.name}-minimal",
                core=core,
                power=PowerType.USB,
                led=led,
                modules=[],
            ))

            module_map = self.get_module_map(core.form_factor)

            # 2. Single module configs (one of each type)
            for cat in ["airiq", "comfort", "presence", "fan_pwm"]:
                if cat in module_map:
                    configs.append(TestConfig(
                        name=f"{core.name}-{cat}",
                        core=core,
                        power=PowerType.USB,
                        led=led,
                        modules=[module_map[cat]],
                    ))

            # 3. Full config (all modules except bathroom for ceiling)
            if core.form_factor == FormFactor.CEILING:
                full_modules = [
                    module_map["airiq"],
                    module_map["comfort"],
                    module_map["presence"],
                    module_map["fan_pwm"],
                ]
            else:
                full_modules = [
                    module_map["airiq"],
                    module_map["comfort"],
                    module_map["presence"],
                    module_map["fan_pwm"],
                ]
            configs.append(TestConfig(
                name=f"{core.name}-full",
                core=core,
                power=PowerType.USB,
                led=led,
                modules=full_modules,
            ))

            # 4. Bathroom config (ceiling only)
            if core.form_factor == FormFactor.CEILING:
                configs.append(TestConfig(
                    name=f"{core.name}-bathroom",
                    core=core,
                    power=PowerType.USB,
                    led=led,
                    modules=[module_map["bathroom"], module_map["comfort"], module_map["presence"]],
                ))

        # Test different power types with one core
        for power in [PowerType.POE, PowerType.PWR]:
            configs.append(TestConfig(
                name=f"CORE_C-{power.name}",
                core=CoreType.CORE_C,
                power=power,
                led=LEDType.LED_CEILING,
                modules=[],
            ))

        return configs


def write_config_file(config: TestConfig, output_dir: Path) -> Path:
    """Write a test config to a file."""
    filename = f"test-{config.get_config_name()}.yaml"
    filepath = output_dir / filename
    filepath.write_text(config.generate_yaml())
    return filepath


def validate_config(config_path: Path, secrets_path: Path) -> Tuple[bool, str]:
    """Validate an ESPHome config file."""
    try:
        result = subprocess.run(
            ["esphome", "config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=config_path.parent,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, "Timeout validating config"
    except Exception as e:
        return False, str(e)


def create_secrets_file(output_dir: Path) -> Path:
    """Create a secrets.yaml file for testing."""
    secrets = {
        "wifi_ssid": "TestNetwork",
        "wifi_password": "TestPassword123",
        "api_encryption_key": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=",
        "ota_password": "test-ota-password",
        "fallback_ap_password": "fallback123",
        "web_username": "admin",
        "web_password": "test_web_password",
    }
    secrets_path = output_dir / "secrets.yaml"
    lines = [f"{k}: \"{v}\"" for k, v in secrets.items()]
    secrets_path.write_text("\n".join(lines))
    return secrets_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate and validate ESPHome test configurations"
    )
    parser.add_argument(
        "--mode",
        choices=["list", "generate", "validate", "matrix"],
        default="list",
        help="Operation mode: list configs, generate files, validate, or output matrix",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate full matrix (all power types and LED options)",
    )
    parser.add_argument(
        "--representative",
        action="store_true",
        help="Generate representative subset for quick CI",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "generated",
        help="Output directory for generated configs",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (for GitHub Actions matrix)",
    )

    args = parser.parse_args()

    # Initialize generator
    generator = ConfigGenerator(
        include_all_power=args.full,
        include_all_led=args.full,
    )

    # Generate configs
    if args.representative:
        configs = generator.generate_representative_configs()
    else:
        configs = generator.generate_all_configs()

    if args.mode == "list":
        if args.json:
            output = {
                "total": len(configs),
                "configs": [c.get_config_name() for c in configs],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Total configurations: {len(configs)}\n")
            for i, config in enumerate(configs, 1):
                print(f"{i:3}. {config.get_config_name()}")
                print(f"      Core: {config.core.name}, Power: {config.power.name}, LED: {config.led.name}")
                print(f"      Modules: {', '.join(m.name for m in config.modules) or 'None'}")

    elif args.mode == "generate":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        secrets_path = create_secrets_file(args.output_dir)
        print(f"Created secrets file: {secrets_path}")

        for config in configs:
            filepath = write_config_file(config, args.output_dir)
            print(f"Generated: {filepath}")

        print(f"\nGenerated {len(configs)} configuration files in {args.output_dir}")

    elif args.mode == "validate":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        secrets_path = create_secrets_file(args.output_dir)

        passed = 0
        failed = 0
        failures = []

        for config in configs:
            filepath = write_config_file(config, args.output_dir)
            success, error = validate_config(filepath, secrets_path)

            if success:
                passed += 1
                print(f"PASS: {config.get_config_name()}")
            else:
                failed += 1
                failures.append((config.get_config_name(), error))
                print(f"FAIL: {config.get_config_name()}")
                if error:
                    for line in error.split("\n")[:5]:
                        print(f"      {line}")

        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed out of {len(configs)}")

        if failures:
            print(f"\nFailed configurations:")
            for name, error in failures:
                print(f"  - {name}")

            sys.exit(1)

    elif args.mode == "matrix":
        # Output format for GitHub Actions matrix
        matrix_configs = []
        for config in configs:
            matrix_configs.append({
                "name": config.get_config_name(),
                "core": config.core.name,
                "power": config.power.name,
                "led": config.led.name,
                "modules": [m.name for m in config.modules],
            })

        output = {"include": matrix_configs}
        print(json.dumps(output))


if __name__ == "__main__":
    main()

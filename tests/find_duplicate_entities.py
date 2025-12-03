#!/usr/bin/env python3
"""
Find duplicate entity names in ESPHome configurations.
This script analyzes all YAML files to find potential entity name conflicts.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


# Custom YAML constructors for ESPHome tags
def esphome_constructor(loader, node):
    """Handle ESPHome custom tags."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Register ESPHome custom tags
for tag in ["!secret", "!include", "!extend", "!lambda", "!remove"]:
    yaml.add_constructor(tag, esphome_constructor, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", esphome_constructor, Loader=yaml.SafeLoader)


class EntityTracker:
    """Track entity definitions across files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        # Maps entity name to list of (file, platform, line_number)
        self.entities: Dict[str, List[Tuple[Path, str, str, int]]] = defaultdict(list)

    def extract_entities(self, file_path: Path):
        """Extract entity definitions from a YAML file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            # Look for entity platforms
            platforms = ['sensor', 'binary_sensor', 'switch', 'button', 'text_sensor',
                        'number', 'select', 'light', 'fan', 'climate', 'cover']

            current_platform = None
            current_line_num = 0

            for line_num, line in enumerate(lines, 1):
                # Check if this is a platform definition
                for platform in platforms:
                    if re.match(rf'^{platform}:', line):
                        current_platform = platform
                        break

                # Look for name definitions
                name_match = re.match(r'\s+name:\s*["\']?([^"\']+)["\']?', line)
                if name_match and current_platform:
                    entity_name = name_match.group(1).strip()

                    # Also look for platform type (e.g., "platform: restart")
                    platform_type = None
                    # Look backwards for platform: line
                    for prev_line_num in range(line_num - 1, max(0, line_num - 10), -1):
                        platform_match = re.match(r'\s+platform:\s*(\w+)', lines[prev_line_num - 1])
                        if platform_match:
                            platform_type = platform_match.group(1)
                            break

                    self.entities[entity_name].append((
                        file_path,
                        current_platform,
                        platform_type or 'unknown',
                        line_num
                    ))

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

    def scan_all_files(self):
        """Scan all YAML files in the repository."""
        dirs = ['products', 'packages', 'base', 'features', 'hardware']

        for dir_name in dirs:
            dir_path = self.repo_root / dir_name
            if not dir_path.exists():
                continue

            for yaml_file in dir_path.rglob('*.yaml'):
                self.extract_entities(yaml_file)

    def find_duplicates(self) -> Dict[str, List[Tuple[Path, str, str, int]]]:
        """Find entity names that appear in multiple files."""
        duplicates = {}

        for entity_name, locations in self.entities.items():
            # Group by file to see if same entity appears multiple times
            files = set(loc[0] for loc in locations)

            # If entity appears in multiple files, it might be a duplicate
            # (unless it's being properly overridden)
            if len(files) > 1:
                duplicates[entity_name] = locations

        return duplicates

    def print_report(self):
        """Print a detailed report of duplicate entities."""
        duplicates = self.find_duplicates()

        if not duplicates:
            print("✅ No duplicate entity names found!")
            return

        print(f"\n⚠️  Found {len(duplicates)} potential duplicate entity names:\n")

        for entity_name, locations in sorted(duplicates.items()):
            print(f"Entity: {entity_name}")
            print(f"  Found in {len(locations)} location(s):")

            for file_path, platform, platform_type, line_num in locations:
                rel_path = file_path.relative_to(self.repo_root)
                print(f"    - {rel_path}:{line_num} ({platform}.{platform_type})")

            print()

        # Special check for restart buttons/switches
        print("\n🔍 Specific Issues Found:\n")

        restart_entities = [name for name in duplicates.keys() if 'restart' in name.lower()]
        if restart_entities:
            print("1. RESTART ENTITY CONFLICTS:")
            print("   The following restart entities have duplicates:")
            for name in restart_entities:
                locations = duplicates[name]
                platforms_used = set(f"{loc[1]}.{loc[2]}" for loc in locations)
                print(f"   - '{name}' defined as: {', '.join(platforms_used)}")

            print("\n   FIX: Remove duplicate restart definitions.")
            print("   Hardware configs (sense360_core_*.yaml) already define button.restart.")
            print("   Remove switch.restart from device_health.yaml")
            print("   Remove redundant button.restart from product configs.")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    tracker = EntityTracker(repo_root)

    print("🔍 Scanning repository for duplicate entity names...\n")
    tracker.scan_all_files()
    tracker.print_report()


if __name__ == "__main__":
    main()

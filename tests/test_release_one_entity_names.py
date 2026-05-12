#!/usr/bin/env python3
"""Lightweight duplicate-entity-name guard for the Release-One profile pair.

The Release-One no-TRIAC product
(``products/sense360-ceiling-poe-ventiq-roomiq.yaml``) includes both:

    - ``packages/features/bathroom_profile.yaml``  (VentIQ display sensors)
    - ``packages/features/comfort_basic_profile.yaml``  (RoomIQ display sensors)

Both profiles expose Home Assistant entities whose names start with
``${friendly_name}``. If both expose a generic name like
``${friendly_name} Temperature``, ESPHome's config validator fails with
``Duplicate sensor entity with name '...'``, which only surfaces at compile
time. This test catches that collision class statically.

Scope is intentionally narrow:

    - only the two profile YAMLs above
    - only top-level entity definitions on those files (``sensor``,
      ``binary_sensor``, ``text_sensor``, ``switch``, ``number``, ``button``)
    - skips entries marked ``internal: true``  (those don't expose to HA)
    - does NOT recurse into ``packages:`` includes (``device_health.yaml``,
      ``diagnostics.yaml``) — those are deliberately shared by both profiles
      and are not the collision class this test targets

Full ESPHome package resolution is not attempted; ``esphome config`` remains
the source of truth for compile-time validation.

Run with:

    python3 tests/test_release_one_entity_names.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Dict, List, Set

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FEATURES_DIR = REPO_ROOT / "packages" / "features"

VENTIQ_PROFILE = FEATURES_DIR / "bathroom_profile.yaml"
ROOMIQ_PROFILE = FEATURES_DIR / "comfort_basic_profile.yaml"

ENTITY_PLATFORM_KEYS = (
    "sensor",
    "binary_sensor",
    "text_sensor",
    "switch",
    "number",
    "button",
)

FRIENDLY_NAME_PLACEHOLDER = "Sense360"


def _esphome_tag(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag, Loader=yaml.SafeLoader)


def _render_name(raw_name: str) -> str:
    """Substitute ``${friendly_name}`` with a fixed placeholder for comparison."""
    return (
        raw_name
        .replace("${friendly_name}", FRIENDLY_NAME_PLACEHOLDER)
        .replace("$friendly_name", FRIENDLY_NAME_PLACEHOLDER)
    )


def _user_facing_names(yaml_path: Path) -> Set[str]:
    """Return the rendered user-facing entity names declared at top level."""
    doc = yaml.safe_load(yaml_path.read_text())
    if not isinstance(doc, dict):
        return set()

    names: Set[str] = set()
    for platform in ENTITY_PLATFORM_KEYS:
        entries = doc.get(platform)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("internal") is True:
                continue
            name = entry.get("name")
            if not isinstance(name, str):
                continue
            names.add(_render_name(name))
    return names


class ReleaseOneEntityNameTests(unittest.TestCase):
    """Static guard against the VentIQ ↔ RoomIQ display-name collision class."""

    def setUp(self) -> None:
        self.assertTrue(
            VENTIQ_PROFILE.is_file(),
            f"missing VentIQ profile at {VENTIQ_PROFILE}",
        )
        self.assertTrue(
            ROOMIQ_PROFILE.is_file(),
            f"missing RoomIQ profile at {ROOMIQ_PROFILE}",
        )

    def test_release_one_profile_names_are_disjoint(self) -> None:
        ventiq_names = _user_facing_names(VENTIQ_PROFILE)
        roomiq_names = _user_facing_names(ROOMIQ_PROFILE)

        self.assertGreater(
            len(ventiq_names),
            0,
            f"no user-facing entity names parsed from {VENTIQ_PROFILE}",
        )
        self.assertGreater(
            len(roomiq_names),
            0,
            f"no user-facing entity names parsed from {ROOMIQ_PROFILE}",
        )

        collisions = sorted(ventiq_names & roomiq_names)
        self.assertEqual(
            collisions,
            [],
            (
                "Release-One profile collision: VentIQ "
                f"({VENTIQ_PROFILE.name}) and RoomIQ "
                f"({ROOMIQ_PROFILE.name}) both expose user-facing entities "
                f"with names: {collisions}. Prefix the colliding names with "
                f"'VentIQ' / 'RoomIQ' so Home Assistant entity registration "
                f"does not collide."
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

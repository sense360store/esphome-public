#!/usr/bin/env python3
"""Static naming proof for WebFlash build entries.

For every entry in ``config/webflash-builds.json``:

    artifact_name == generate_webflash_filename(
        basename(product_yaml without .yaml),
        version,
        channel,
    )

This locks the contract that the rename step in
``.github/workflows/firmware-build-release.yml`` (which calls
``scripts/product_name_mapper.py``) will produce exactly the
``artifact_name`` declared in ``config/webflash-builds.json``.

Plus three explicit Release-One assertions so the canonical
``Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin``
name cannot drift silently.

FanTRIAC is intentionally excluded from production Release-One while HW-005
is open (see docs/release-one-hardware-audit.md#fantriac-mapping-resolution).
The FanTRIAC product YAML is retained as a blocked/reference file but is not
in the WebFlash build matrix.

Run with:

    python3 tests/test_webflash_artifact_naming.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from product_name_mapper import (  # noqa: E402
    convert_product_name,
    generate_webflash_filename,
)

BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

RELEASE_ONE_CANONICAL_PRODUCT = "sense360-ceiling-poe-ventiq-roomiq"
RELEASE_ONE_WEBFLASH_BASENAME = "ceiling-poe-ventiq-roomiq"
RELEASE_ONE_DISPLAY_NAME = "Sense360-Ceiling-POE-VentIQ-RoomIQ"
RELEASE_ONE_ARTIFACT = (
    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
)


def _load_builds():
    return json.loads(BUILDS_PATH.read_text())["builds"]


def _product_key(product_yaml: str) -> str:
    """Reproduce the build-time product key the workflow will pass to the mapper.

    ``firmware-build-release.yml`` derives ``matrix.product`` from
    ``basename(product_yaml, .yaml)``. The mapper accepts either the canonical
    ``sense360-`` prefix or the bare WebFlash basename (``products/webflash/``
    wrapper) and produces the same WebFlash display name.
    """
    return Path(product_yaml).stem


class WebflashArtifactNamingTests(unittest.TestCase):
    def test_release_one_canonical_product_maps_to_display_name(self):
        self.assertEqual(
            convert_product_name(RELEASE_ONE_CANONICAL_PRODUCT),
            RELEASE_ONE_DISPLAY_NAME,
        )

    def test_release_one_webflash_basename_maps_to_display_name(self):
        self.assertEqual(
            convert_product_name(RELEASE_ONE_WEBFLASH_BASENAME),
            RELEASE_ONE_DISPLAY_NAME,
        )

    def test_release_one_filename_is_locked(self):
        self.assertEqual(
            generate_webflash_filename(
                RELEASE_ONE_CANONICAL_PRODUCT, "1.0.0", "stable"
            ),
            RELEASE_ONE_ARTIFACT,
        )

    def test_every_build_entry_artifact_name_matches_mapper(self):
        builds = _load_builds()
        self.assertGreater(len(builds), 0, "no builds declared in webflash-builds.json")
        for entry in builds:
            with self.subTest(config_string=entry.get("config_string")):
                product_key = _product_key(entry["product_yaml"])
                produced = generate_webflash_filename(
                    product_key, entry["version"], entry["channel"]
                )
                self.assertEqual(
                    produced,
                    entry["artifact_name"],
                    (
                        f"mapper produced {produced!r} for "
                        f"{product_key!r} v{entry['version']} {entry['channel']}; "
                        f"webflash-builds.json declares {entry['artifact_name']!r}"
                    ),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

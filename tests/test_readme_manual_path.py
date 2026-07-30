#!/usr/bin/env python3
"""README manual-path accuracy guards (REPO-CONSOLIDATION-001 closing pass).

The repository README's manual / custom path example is the one place a
customer copies a `packages:` block from. These guards pin it to the
declarations so it can never go stale silently again:

  * the example's `ref:` tag matches ``v{version}`` of the production
    baseline's stable row in ``config/webflash-builds.json`` (the release
    matrix is the declaration of what ships, per ESP-007);
  * the example's `files:` entry is the production baseline's customer
    ``product_yaml`` from ``config/product-catalog.json`` (the tag-pinned
    shim path customers must never lose);
  * the tag-pinned example carries no ``refresh:`` key (a pinned tag never
    changes, so a refresh interval is noise that invites `ref: main` habits);
  * the ESPHome badge version equals the ``esphome`` pin in
    ``requirements-dev.txt`` (the pin is the source of truth; the badge
    tracks it).

The production baseline is located by declaration, not hardcoded: it is the
catalog entry with ``hardware_status: verified-for-release-one`` (exactly one
must exist; ``status: production`` alone is not unique — the waiver-promoted
Bedroom stable is also production).

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_readme_manual_path.py
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS = REPO_ROOT / "config" / "webflash-builds.json"
REQUIREMENTS_DEV = REPO_ROOT / "requirements-dev.txt"


def _production_baseline() -> dict:
    catalog = json.loads(PRODUCT_CATALOG.read_text(encoding="utf-8"))
    entries = catalog["products"] if isinstance(catalog, dict) else catalog
    production = [
        e
        for e in entries
        if isinstance(e, dict)
        and e.get("hardware_status") == "verified-for-release-one"
    ]
    if len(production) != 1:
        raise AssertionError(
            "expected exactly one hardware_status: verified-for-release-one "
            f"catalog entry (the Release-One baseline), found {len(production)}"
        )
    return production[0]


def _stable_build_row(config_string: str) -> dict:
    builds = json.loads(WEBFLASH_BUILDS.read_text(encoding="utf-8"))["builds"]
    rows = [
        b
        for b in builds
        if b.get("config_string") == config_string
        and b.get("channel") == "stable"
    ]
    if len(rows) != 1:
        raise AssertionError(
            f"expected exactly one stable build row for {config_string}, "
            f"found {len(rows)}"
        )
    return rows[0]


def _readme_example_block() -> str:
    """The first fenced YAML block containing the remote packages example."""
    text = README.read_text(encoding="utf-8")
    for match in re.finditer(r"```yaml\n(.*?)```", text, re.DOTALL):
        if "sense360_firmware" in match.group(1):
            return match.group(1)
    raise AssertionError(
        "README.md no longer contains the manual-path packages example "
        "(a ```yaml block with a sense360_firmware package)"
    )


class ReadmeManualPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = _production_baseline()
        cls.stable = _stable_build_row(cls.baseline["config_string"])
        cls.block = _readme_example_block()

    def test_example_ref_is_the_stable_release_tag(self) -> None:
        match = re.search(r"ref:\s*(\S+)", self.block)
        self.assertIsNotNone(match, "example must pin a ref:")
        expected = f"v{self.stable['version']}"
        self.assertEqual(
            match.group(1),
            expected,
            "README manual-path example must pin the production baseline's "
            f"current stable tag {expected} (from config/webflash-builds.json)",
        )

    def test_example_files_is_the_customer_product_yaml(self) -> None:
        self.assertIn(
            self.baseline["product_yaml"],
            self.block,
            "README manual-path example must reference the production "
            f"baseline's customer path {self.baseline['product_yaml']}",
        )

    def test_tag_pinned_example_has_no_refresh(self) -> None:
        self.assertNotIn(
            "refresh:",
            self.block,
            "a tag-pinned example must not carry refresh: — a release tag "
            "never changes",
        )

    def test_esphome_badge_matches_the_dev_pin(self) -> None:
        pin = None
        for line in REQUIREMENTS_DEV.read_text(encoding="utf-8").splitlines():
            match = re.match(r"esphome\s*>=\s*([\w.]+)", line.strip())
            if match:
                pin = match.group(1)
        self.assertIsNotNone(pin, "requirements-dev.txt must pin esphome>=")
        badge = re.search(
            r"img\.shields\.io/badge/ESPHome-([\w.]+)%2B", README.read_text(encoding="utf-8")
        )
        self.assertIsNotNone(badge, "README must carry the ESPHome badge")
        self.assertEqual(
            badge.group(1),
            pin,
            "README ESPHome badge must equal the requirements-dev.txt pin "
            f"(esphome>={pin})",
        )


if __name__ == "__main__":
    unittest.main()

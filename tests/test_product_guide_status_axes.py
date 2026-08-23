#!/usr/bin/env python3
"""Product-guide status axes guard (SENSE360-CANONICALISATION-001 PR 16).

The customer product guides carry a labelled "Product status" section
separating four fact axes: commercial availability, firmware lifecycle,
installer (WebFlash) availability, and hardware evidence. This module pins:

* every served product page carries the section and all four axis labels;
* the channel words in the two machine-decidable axes match the
  declarations (``config/product-catalog.json`` per config string), so the
  rendered lifecycle can never drift from the catalog;
* no product page carries commerce language (a stable channel must never
  read as buyability — commercial truth is owned by SOT, never authored
  here);
* the hand-written channel badge and the "Channel:" admonition on each
  guide (and the guide's badge on the product index) match the same
  declared channel, so the rendered channel can never contradict the
  Product status section (found drifted once: the Kitchen guide read
  ``stable`` on a ``preview`` config);
* the setup-hotspot name each guide prints matches the firmware's own
  ``fallback_ssid`` substitution, so the documented hotspot can never
  drift from the SSID the build actually broadcasts (found drifted once:
  every guide printed the ``${device_name} FB`` package default, which
  no product build uses);
* the product-taxonomy board table stays consistent with
  ``config/hardware-catalog.json`` (SKU and friendly name), so the
  hand-written projection can never drift from the machine catalog.

Run with::

    python3 tests/test_product_guide_status_axes.py
"""

import json
import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"
TAXONOMY = REPO_ROOT / "docs" / "product-taxonomy.md"
PAGES_DIR = REPO_ROOT / "site" / "docs" / "products"
PRODUCTS_DIR = REPO_ROOT / "products"


def _esphome_tag(loader, node):  # pragma: no cover - trivial passthrough
    return None


# Product YAML carries ESPHome custom tags; the substitutions block this
# module reads is plain YAML, so the tags only need to parse, not resolve.
for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag, Loader=yaml.SafeLoader)

# Page file -> served config string (the same mapping the entity-table
# generator serves; a new served product page must be added here).
PAGE_CONFIGS = {
    "ceiling-poe-roomiq.md": "Ceiling-POE-RoomIQ",
    "ceiling-poe-airiq-roomiq.md": "Ceiling-POE-AirIQ-RoomIQ",
    "ceiling-poe-ventiq-roomiq.md": "Ceiling-POE-VentIQ-RoomIQ",
    "ceiling-poe-ventiq-roomiq-led.md": "Ceiling-POE-VentIQ-RoomIQ-LED",
}

AXIS_LABELS = (
    "**Commercial availability**",
    "**Firmware lifecycle**",
    "**Installer availability**",
    "**Hardware evidence**",
)

# Commerce language that must never appear on a customer product page —
# commercial truth is SOT's, and served firmware never implies buyability.
COMMERCE_PATTERNS = (
    re.compile(r"\bbuy now\b", re.IGNORECASE),
    re.compile(r"\bfor sale\b", re.IGNORECASE),
    re.compile(r"\badd to cart\b", re.IGNORECASE),
    re.compile(r"\bon sale\b", re.IGNORECASE),
    re.compile(r"\bpurchase\b", re.IGNORECASE),
)


def catalog_by_config():
    products = json.loads(PRODUCT_CATALOG.read_text(encoding="utf-8"))["products"]
    return {p["config_string"]: p for p in products if "config_string" in p}


class ProductStatusAxesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog_by_config()

    def test_every_page_carries_the_four_axes(self):
        for filename in PAGE_CONFIGS:
            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")
            self.assertIn("## Product status", raw, filename)
            for label in AXIS_LABELS:
                self.assertIn(label, raw, f"{filename}: missing {label}")

    def test_lifecycle_axis_matches_the_catalog_channel(self):
        for filename, config_string in PAGE_CONFIGS.items():
            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")
            channel = self.catalog[config_string]["channel"]
            self.assertIn(channel, ("stable", "preview"), config_string)
            section = raw.split("## Product status", 1)[1].split("\n## ", 1)[0]
            if channel == "stable":
                self.assertIn("**stable**", section, filename)
                self.assertNotIn("**preview**", section, filename)
            else:
                self.assertIn("**preview**", section, filename)
                self.assertIn("acknowledge", section, filename)

    def test_channel_badge_and_admonition_match_the_catalog_channel(self):
        # The lifecycle axis is already pinned above, but the badge under
        # the page title, the "Channel:" admonition, and the badge on the
        # product index are three separate hand-written renderings of the
        # same fact. All three drifted out of agreement with the Product
        # status section once, presenting a preview config as the
        # supported stable customer firmware.
        index = (PAGES_DIR / "index.md").read_text(encoding="utf-8")
        for filename, config_string in PAGE_CONFIGS.items():
            channel = self.catalog[config_string]["channel"]
            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")

            badge = re.search(r's360-badge--(\w+)">(\w+)</span>', raw)
            self.assertIsNotNone(badge, f"{filename}: no channel badge")
            self.assertEqual(
                (badge.group(1), badge.group(2)),
                (channel, channel),
                f"{filename}: badge {badge.group(2)!r} but the catalog "
                f"declares {channel!r}",
            )

            admonition = re.search(r'!!! \w+ "Channel: (\w+)"', raw)
            self.assertIsNotNone(admonition, f"{filename}: no Channel admonition")
            self.assertEqual(
                admonition.group(1),
                channel,
                f"{filename}: Channel admonition {admonition.group(1)!r} "
                f"but the catalog declares {channel!r}",
            )

            stem = filename[: -len(".md")]
            index_badge = re.search(
                rf"\]\({re.escape(stem)}\.md\)\*\*\s*\n\s*"
                rf'<span class="s360-badge s360-badge--(\w+)">',
                index,
            )
            self.assertIsNotNone(index_badge, f"index.md: no badge for {stem}")
            self.assertEqual(
                index_badge.group(1),
                channel,
                f"index.md badges {stem} as {index_badge.group(1)!r} but "
                f"the catalog declares {channel!r}",
            )

    def test_setup_hotspot_name_matches_the_firmware_fallback_ssid(self):
        # Every guide prints the name of the fallback AP the device
        # broadcasts when it cannot join a network. Each product YAML
        # overrides `fallback_ssid`, so the `${device_name} FB` default in
        # packages/base/wifi.yaml never reaches a shipped build — the
        # guides printed that default anyway until this pin was added.
        for filename in PAGE_CONFIGS:
            stem = filename[: -len(".md")]
            product = PRODUCTS_DIR / f"sense360-{stem}.yaml"
            self.assertTrue(product.is_file(), f"{filename}: {product} missing")
            subs = yaml.safe_load(product.read_text(encoding="utf-8"))["substitutions"]
            expected = subs.get("fallback_ssid")
            self.assertTrue(
                expected,
                f"{product.name}: no fallback_ssid override to pin against",
            )

            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")
            documented = re.search(r"setup hotspot named `([^`]+)`", raw)
            self.assertIsNotNone(documented, f"{filename}: no setup hotspot name")
            self.assertEqual(
                documented.group(1),
                expected,
                f"{filename}: documents the setup hotspot as "
                f"{documented.group(1)!r} but the firmware broadcasts "
                f"{expected!r}",
            )

    def test_commercial_axis_claims_nothing_and_pages_carry_no_commerce(self):
        for filename in PAGE_CONFIGS:
            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")
            self.assertIn("not currently\n  sold", raw, filename)
            for pattern in COMMERCE_PATTERNS:
                self.assertIsNone(pattern.search(raw), f"{filename}: {pattern.pattern}")

    def test_axes_declare_their_independence(self):
        for filename in PAGE_CONFIGS:
            raw = (PAGES_DIR / filename).read_text(encoding="utf-8")
            self.assertIn("separate axes", raw, filename)


class TaxonomyBoardTableTests(unittest.TestCase):
    def test_taxonomy_table_rows_match_the_hardware_catalog(self):
        # The taxonomy board table is a hand-written projection (it adds the
        # config-token axis the catalog does not carry); this pin keeps its
        # SKU and friendly-name columns from drifting from the machine
        # catalog, which stays the single source of board identity.
        doc = json.loads(HARDWARE_CATALOG.read_text(encoding="utf-8"))
        rows = doc["items"]
        names = {h["sku"]: h["friendly_name"] for h in rows if isinstance(h, dict)}
        table_rows = re.findall(
            r"^\|\s*(S360-\d+)\s*\|\s*([^|]+?)\s*\|",
            TAXONOMY.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        self.assertGreater(len(table_rows), 5)
        for sku, name in table_rows:
            self.assertIn(sku, names, sku)
            self.assertEqual(name, names[sku], sku)


if __name__ == "__main__":
    unittest.main()

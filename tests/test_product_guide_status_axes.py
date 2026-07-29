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

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"
TAXONOMY = REPO_ROOT / "docs" / "product-taxonomy.md"
PAGES_DIR = REPO_ROOT / "site" / "docs" / "products"

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

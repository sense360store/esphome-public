#!/usr/bin/env python3
"""device_sku canonicalisation guard (SENSE360-CANONICALISATION-001 PR 07).

The ``device_sku`` substitution feeds the customer-visible "Product SKU"
diagnostic text sensor (``s360_product_sku``,
tests/test_static_diagnostic_publish.py owns the publication mechanics).
Before PR 07 it carried the pre-catalog legacy identifiers
``S360-CORE-C`` / ``S360-CORE-C-POE`` / ``S360-CORE-C-USB`` — a second,
non-canonical configuration-layer identifier on no catalog axis
(recorded as a PR 07 input by the PR 06 contract,
docs/sense360-canonicalisation-001-pr06-contract.md §8).

PR 07 rebinds every declaration to the canonical board SKU of the
flashable hub (``S360-100`` — every flashable device is a Core); power
and mount facts stay published through the canonical config string.
This module pins the resolution:

  * every ``device_sku`` substitution in ``products/`` carries a SKU
    that exists in config/hardware-catalog.json (the machine-readable
    canonical SKU catalog);
  * the retired ``S360-CORE-C*`` scheme never returns as a
    ``device_sku`` value.

Run with::

    python3 tests/test_device_sku_canonical.py
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"

DEVICE_SKU_LINE = re.compile(r"^\s*device_sku:\s*(?P<value>\S+)\s*$", re.M)


def _catalog_skus() -> set:
    data = json.loads(HARDWARE_CATALOG.read_text(encoding="utf-8"))
    return {item["sku"] for item in data["items"]}


def _device_sku_declarations() -> list:
    found = []
    for path in sorted((REPO_ROOT / "products").rglob("*.yaml")):
        # Skip build caches (e.g. products/.esphome/ from a local
        # `esphome config/compile` run) - only tracked tree content counts.
        if any(part.startswith(".") for part in path.parts):
            continue
        for match in DEVICE_SKU_LINE.finditer(path.read_text(encoding="utf-8")):
            value = match.group("value").strip("\"'")
            found.append((path.relative_to(REPO_ROOT), value))
    return found


class DeviceSkuCanonicalTests(unittest.TestCase):
    def test_declarations_exist(self) -> None:
        # The guard is vacuous if the substitution disappears silently;
        # removing the Product SKU surface is a deliberate decision, not
        # a side effect.
        self.assertTrue(_device_sku_declarations())

    def test_every_device_sku_is_a_catalog_sku(self) -> None:
        skus = _catalog_skus()
        for rel, value in _device_sku_declarations():
            with self.subTest(product=str(rel)):
                self.assertIn(
                    value,
                    skus,
                    f"device_sku {value!r} in {rel} is not a canonical "
                    "config/hardware-catalog.json SKU; the pre-catalog "
                    "S360-CORE-C* scheme was retired by "
                    "SENSE360-CANONICALISATION-001 PR 07.",
                )

    def test_retired_scheme_never_returns(self) -> None:
        for rel, value in _device_sku_declarations():
            with self.subTest(product=str(rel)):
                self.assertFalse(
                    value.startswith("S360-CORE-C"),
                    f"retired legacy identifier {value!r} returned in {rel}",
                )


if __name__ == "__main__":
    unittest.main()

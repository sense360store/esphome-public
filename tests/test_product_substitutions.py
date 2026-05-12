#!/usr/bin/env python3
"""Static substitution checks for products/*.yaml.

Catches ESPHome configuration errors that only show up at compile time, before
they reach the build matrix:

    - hostname (``device_name``) must be <= 31 characters and match
      ``^[a-z0-9-]+$``  (ESPHome 2026.x hostname rule)
    - fallback AP SSID (effective) must be <= 32 characters
    - fallback AP password literal must be 8..64 characters if present
      (``!secret`` values are skipped — secrets are validated at runtime, not
      here)

The "effective" fallback SSID is derived as:

    1. a literal top-level ``wifi.ap.ssid`` override on the product YAML, if it
       does not contain a ``${...}`` substitution token
    2. else ``substitutions.fallback_ssid`` (with any ``${device_name}`` token
       expanded against the product's own ``device_name``)
    3. else the base-wifi default ``${device_name} FB`` -> ``"<device_name> FB"``

Excluded from scanning:

    - ``products/secrets.yaml``           (template / not a product config)
    - ``products/webflash/*.yaml``        (thin re-export wrappers; canonical
                                            product YAML is checked instead)

Run with:

    python3 tests/test_product_substitutions.py
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = REPO_ROOT / "products"

DEVICE_NAME_MAX = 31
SSID_MAX = 32
AP_PASSWORD_MIN = 8
AP_PASSWORD_MAX = 64

DEVICE_NAME_RE = re.compile(r"^[a-z0-9-]+$")


def _esphome_tag(loader, node):
    """Reduce ESPHome custom tags to plain Python values for static parsing."""
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


def _collect_product_files() -> list[Path]:
    """Return product YAMLs in scope: top-level products/*.yaml minus excludes."""
    files = []
    for path in sorted(PRODUCTS_DIR.glob("*.yaml")):
        if path.name == "secrets.yaml":
            continue
        files.append(path)
    return files


def _load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    return data if isinstance(data, dict) else {}


def _wifi_ap_ssid_override(doc: Dict[str, Any]) -> Optional[str]:
    """Literal top-level ``wifi.ap.ssid`` if the product sets one, else None.

    A value containing ``${...}`` is treated as not-a-literal-override and
    falls through to the substitution-based path.
    """
    wifi = doc.get("wifi")
    if not isinstance(wifi, dict):
        return None
    ap = wifi.get("ap")
    if not isinstance(ap, dict):
        return None
    ssid = ap.get("ssid")
    if not isinstance(ssid, str):
        return None
    if "${" in ssid or "$" + "device_name" in ssid:
        return None
    return ssid


def _effective_fallback_ssid(
    device_name: Optional[str],
    fallback_ssid_sub: Optional[str],
    wifi_ap_override: Optional[str],
) -> Optional[str]:
    if wifi_ap_override is not None:
        return wifi_ap_override
    if isinstance(fallback_ssid_sub, str):
        return (
            fallback_ssid_sub
            .replace("${device_name}", device_name or "")
            .replace("$device_name", device_name or "")
        )
    if device_name is not None:
        return f"{device_name} FB"
    return None


class ProductSubstitutionTests(unittest.TestCase):
    """Per-product static checks for hostname / fallback AP credentials."""

    def setUp(self) -> None:
        self.products = _collect_product_files()
        self.assertGreater(
            len(self.products),
            0,
            f"no product YAMLs discovered under {PRODUCTS_DIR}",
        )

    def test_device_name_length_and_charset(self) -> None:
        for path in self.products:
            with self.subTest(product=path.relative_to(REPO_ROOT)):
                doc = _load_yaml(path)
                subs = doc.get("substitutions") or {}
                device_name = subs.get("device_name")
                if device_name is None:
                    # Legacy product without a ``device_name`` substitution
                    # exposes nothing for the hostname rule to bite on.
                    continue
                self.assertIsInstance(
                    device_name,
                    str,
                    f"{path.name}: device_name must be a string",
                )
                self.assertLessEqual(
                    len(device_name),
                    DEVICE_NAME_MAX,
                    (
                        f"{path.name}: device_name length "
                        f"{len(device_name)} > {DEVICE_NAME_MAX} "
                        f"(ESPHome hostname limit). value={device_name!r}"
                    ),
                )
                self.assertRegex(
                    device_name,
                    DEVICE_NAME_RE,
                    (
                        f"{path.name}: device_name {device_name!r} must match "
                        f"{DEVICE_NAME_RE.pattern} (lowercase alnum + hyphen)"
                    ),
                )

    def test_fallback_ssid_effective_length(self) -> None:
        for path in self.products:
            with self.subTest(product=path.relative_to(REPO_ROOT)):
                doc = _load_yaml(path)
                subs = doc.get("substitutions") or {}
                device_name = subs.get("device_name")
                fallback_ssid_sub = subs.get("fallback_ssid")
                wifi_override = _wifi_ap_ssid_override(doc)
                effective = _effective_fallback_ssid(
                    device_name, fallback_ssid_sub, wifi_override
                )
                if effective is None:
                    # No device_name and no SSID override => nothing to check.
                    continue
                self.assertLessEqual(
                    len(effective),
                    SSID_MAX,
                    (
                        f"{path.name}: effective fallback AP SSID length "
                        f"{len(effective)} > {SSID_MAX}. "
                        f"value={effective!r}. "
                        f"Set substitutions.fallback_ssid or wifi.ap.ssid to "
                        f"a shorter literal."
                    ),
                )

    def test_fallback_ap_password_literal_length(self) -> None:
        for path in self.products:
            with self.subTest(product=path.relative_to(REPO_ROOT)):
                doc = _load_yaml(path)
                subs = doc.get("substitutions") or {}
                pwd = subs.get("fallback_ap_password")
                if pwd is None:
                    continue
                if not isinstance(pwd, str):
                    self.fail(
                        f"{path.name}: fallback_ap_password must be a string "
                        f"if present"
                    )
                if pwd.startswith("!secret"):
                    # ``!secret``-driven passwords are validated at runtime
                    # against the actual secrets file; skip here.
                    continue
                self.assertGreaterEqual(
                    len(pwd),
                    AP_PASSWORD_MIN,
                    (
                        f"{path.name}: fallback_ap_password literal length "
                        f"{len(pwd)} < {AP_PASSWORD_MIN}"
                    ),
                )
                self.assertLessEqual(
                    len(pwd),
                    AP_PASSWORD_MAX,
                    (
                        f"{path.name}: fallback_ap_password literal length "
                        f"{len(pwd)} > {AP_PASSWORD_MAX}"
                    ),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

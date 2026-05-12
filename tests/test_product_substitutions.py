#!/usr/bin/env python3
"""Lightweight preflight checks on product substitutions.

This catches mistakes that would otherwise only surface during a full
ESPHome config validation (or, worse, only during firmware build):

* Fallback AP SSIDs longer than 32 characters (ESPHome rejects them).
* Fallback AP passwords with invalid length (ESPHome requires 8-64 chars).
* device_name values that are empty, too long, or not DNS-safe.

It does NOT require ESPHome to be installed. It loads each product YAML
with PyYAML using the same custom-tag handling as ``tests/validate_configs.py``
so ESPHome's ``!include`` / ``!secret`` / ``!lambda`` / ``!extend`` /
``!remove`` tags don't break parsing.

Scope:
* All files under ``products/*.yaml``.
* Excludes ``products/secrets.yaml`` (an !include shim) and
  ``products/webflash/*.yaml`` (thin WebFlash wrappers that re-export a
  canonical product YAML via !include — checked transitively through
  their canonical target).

Effective fallback AP SSID resolution (mirrors how ESPHome merges
``packages/base/wifi.yaml``):

1. If the product defines a literal top-level ``wifi.ap.ssid`` (no
   ``${...}`` substitution reference), that wins.
2. Else, if ``substitutions.fallback_ssid`` is present, use it, resolving
   any ``${device_name}`` reference against ``substitutions.device_name``.
3. Else, if ``substitutions.device_name`` is present and non-empty, fall
   back to the package default pattern ``"${device_name} FB"``.
4. Else, skip the SSID-length check for that product. (Template products
   expect the user to supply ``device_name`` in their own config.)

Exit code is non-zero if any product fails any check.
"""

import re
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = REPO_ROOT / "products"

MAX_SSID_LEN = 32
MIN_AP_PASSWORD_LEN = 8
MAX_AP_PASSWORD_LEN = 64
MAX_DEVICE_NAME_LEN = 63
DEVICE_NAME_RE = re.compile(r"^[a-z0-9-]+$")
SUBST_RE = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _esphome_tag_constructor(loader, node):
    """Accept ESPHome custom tags without resolving them."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(tag, _esphome_tag_constructor, Loader=yaml.SafeLoader)
yaml.add_multi_constructor("!include_dir_", _esphome_tag_constructor, Loader=yaml.SafeLoader)


def _discover_products():
    """Return the list of product YAML files to check."""
    files = []
    for path in sorted(PRODUCTS_DIR.glob("*.yaml")):
        if path.name == "secrets.yaml":
            continue
        files.append(path)
    return files


def _load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _is_literal_string(value):
    """A literal string is a non-empty str with no ${...} placeholders."""
    return isinstance(value, str) and value != "" and SUBST_RE.search(value) is None


def _resolve_simple_substitution(value, substitutions):
    """Resolve ${name} references where the referent is a literal string."""
    if not isinstance(value, str):
        return value

    def replace(match):
        key = match.group(1)
        sub = substitutions.get(key)
        if isinstance(sub, str):
            return sub
        return match.group(0)

    return SUBST_RE.sub(replace, value)


def _top_level_wifi_ap_ssid(config):
    wifi = config.get("wifi") if isinstance(config, dict) else None
    if not isinstance(wifi, dict):
        return None
    ap = wifi.get("ap")
    if not isinstance(ap, dict):
        return None
    return ap.get("ssid")


def _effective_fallback_ssid(config, substitutions):
    """Return (ssid_or_none, source) following the resolution rules."""
    top_level_ssid = _top_level_wifi_ap_ssid(config)
    if _is_literal_string(top_level_ssid):
        return top_level_ssid, "wifi.ap.ssid override"

    if "fallback_ssid" in substitutions:
        raw = substitutions["fallback_ssid"]
        if isinstance(raw, str):
            resolved = _resolve_simple_substitution(raw, substitutions)
            return resolved, "substitutions.fallback_ssid"

    device_name = substitutions.get("device_name")
    if isinstance(device_name, str) and device_name.strip() != "":
        return f"{device_name} FB", "default '${device_name} FB'"

    return None, None


class Checker:
    def __init__(self):
        self.errors = []
        self.checked = 0
        self.skipped_ssid = []

    def fail(self, path, msg):
        self.errors.append(f"{path.relative_to(REPO_ROOT)}: {msg}")

    def check_file(self, path):
        try:
            config = _load_yaml(path)
        except yaml.YAMLError as e:
            self.fail(path, f"YAML parse error - {e}")
            return
        except Exception as e:
            self.fail(path, f"Read error - {e}")
            return

        if not isinstance(config, dict):
            self.fail(path, "Top-level YAML is not a mapping")
            return

        substitutions = config.get("substitutions") or {}
        if not isinstance(substitutions, dict):
            self.fail(path, "'substitutions' must be a mapping")
            return

        self.checked += 1
        self._check_device_name(path, substitutions)
        self._check_fallback_ap_password(path, substitutions)
        self._check_fallback_ssid(path, config, substitutions)

    def _check_device_name(self, path, substitutions):
        if "device_name" not in substitutions:
            return
        value = substitutions["device_name"]
        if not isinstance(value, str) or value.strip() == "":
            self.fail(path, "'device_name' is empty")
            return
        if len(value) > MAX_DEVICE_NAME_LEN:
            self.fail(
                path,
                f"'device_name' = {value!r} length {len(value)} > {MAX_DEVICE_NAME_LEN}",
            )
        if not DEVICE_NAME_RE.match(value):
            self.fail(
                path,
                f"'device_name' = {value!r} must match {DEVICE_NAME_RE.pattern} "
                "(lowercase letters, digits, hyphens only)",
            )

    def _check_fallback_ap_password(self, path, substitutions):
        if "fallback_ap_password" not in substitutions:
            return
        value = substitutions["fallback_ap_password"]
        if not isinstance(value, str):
            return
        if not _is_literal_string(value):
            return
        length = len(value)
        if length < MIN_AP_PASSWORD_LEN or length > MAX_AP_PASSWORD_LEN:
            self.fail(
                path,
                f"'fallback_ap_password' length {length} outside "
                f"[{MIN_AP_PASSWORD_LEN}, {MAX_AP_PASSWORD_LEN}]",
            )

    def _check_fallback_ssid(self, path, config, substitutions):
        ssid, source = _effective_fallback_ssid(config, substitutions)
        if ssid is None:
            self.skipped_ssid.append(path)
            return
        if SUBST_RE.search(ssid):
            return
        if len(ssid) > MAX_SSID_LEN:
            self.fail(
                path,
                f"fallback AP SSID {ssid!r} (from {source}) length "
                f"{len(ssid)} > {MAX_SSID_LEN}",
            )


def main():
    files = _discover_products()
    if not files:
        print(f"No product YAMLs found under {PRODUCTS_DIR}", file=sys.stderr)
        return 1

    print(f"Preflight check on {len(files)} product YAMLs under {PRODUCTS_DIR.relative_to(REPO_ROOT)}/")
    checker = Checker()
    for path in files:
        checker.check_file(path)

    print("")
    print(f"Products inspected: {checker.checked}")
    if checker.skipped_ssid:
        print(
            f"SSID check skipped for {len(checker.skipped_ssid)} template product(s) "
            "without a device_name (user supplies it):"
        )
        for path in checker.skipped_ssid:
            print(f"  - {path.relative_to(REPO_ROOT)}")
    print("")

    if checker.errors:
        print(f"FAIL: {len(checker.errors)} problem(s) found:")
        for err in checker.errors:
            print(f"  - {err}")
        return 1

    print("OK: all product substitutions pass preflight checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

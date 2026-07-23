#!/usr/bin/env python3
"""CORE-FRAMEWORK-001 — shared Sense360 firmware / entity framework contract.

These tests define (and then pin) the shared device framework that every
production bundle composes in:

* ``config/core-framework.json`` — the machine-readable framework contract
  (capability registry, module-status contract, device-health contract, and
  the per-config-string compile-time capability declarations). Per repo
  convention, docs describe; ``config/`` decides.
* ``packages/base/device_framework.yaml`` — the single reusable ESPHome
  package that exposes the shared identity / capability / module-status /
  health entities. It is included exactly once per bundle (never by feature
  profiles, board packages, compile-only skeletons, or the bench harness).
* the per-bundle ``s360_*`` substitution block that declares the bundle's
  compile-time capabilities, cross-checked against the contract file and
  against ``config/product-catalog.json`` module declarations.

Contract highlights enforced here:

* Capability values are **compile-time composition facts only** — no runtime
  hardware autodetection is claimed anywhere.
* Module status uses the smallest accurate value set today
  (``Not included`` / ``Included``); the richer runtime set (Initialising /
  Available / Degraded / Unavailable / Fault) is documented as **reserved**
  and must NOT be emitted by this framework until a module-specific PR
  provides a real runtime health signal.
* Shared entities carry stable ``s360_``-prefixed IDs, product-facing names
  without ``${friendly_name}`` duplication, ``entity_category: diagnostic``,
  and technical entities are disabled by default.
* No secret / credential material is exposed by the framework.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_core_framework.py

or::

    python3 -m unittest tests.test_core_framework -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CONTRACT_PATH = REPO_ROOT / "config" / "core-framework.json"
FRAMEWORK_PACKAGE_REL = "packages/base/device_framework.yaml"
FRAMEWORK_PACKAGE = REPO_ROOT / FRAMEWORK_PACKAGE_REL
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"
COMPILE_ONLY_DIR = REPO_ROOT / "products" / "compile-only"
HARDWARE_CATALOG = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG = REPO_ROOT / "config" / "product-catalog.json"

# --- Expected framework surface --------------------------------------------

# Stable machine-readable capability identifiers. These may never be renamed
# once shipped; extend by addition only.
EXPECTED_CAPABILITY_IDS = {
    "core",
    "power_poe",
    "power_usb",
    "roomiq",
    "airiq",
    "ventiq",
    "presence",
    "led",
    "fan_relay",
    "fan_pwm",
    "fan_dac",
    "fan_triac",
}

CAPABILITY_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# Module-status slots exposed as entities (module key -> substitution key).
MODULE_STATUS_SUBSTITUTIONS = {
    "roomiq": "s360_module_roomiq",
    "airiq": "s360_module_airiq",
    "ventiq": "s360_module_ventiq",
    "presence": "s360_module_presence",
    "led": "s360_module_led",
    "fan_control": "s360_module_fan_control",
}

# Capability id -> module-status key it drives (power/platform caps drive none).
CAPABILITY_TO_MODULE = {
    "roomiq": "roomiq",
    "airiq": "airiq",
    "ventiq": "ventiq",
    "presence": "presence",
    "led": "led",
    "fan_relay": "fan_control",
    "fan_pwm": "fan_control",
    "fan_dac": "fan_control",
    "fan_triac": "fan_control",
}

# Config-string token -> capability ids it implies (and vice versa).
TOKEN_CAPABILITIES = {
    "POE": {"power_poe"},
    "USB": {"power_usb"},
    "RoomIQ": {"roomiq", "presence"},
    "AirIQ": {"airiq"},
    "VentIQ": {"ventiq"},
    "LED": {"led"},
    "FanRelay": {"fan_relay"},
    "FanPWM": {"fan_pwm"},
    "FanDAC": {"fan_dac"},
    "FanTRIAC": {"fan_triac"},
}

# Compile-time module status values (the smallest accurate set today).
ALLOWED_MODULE_STATUS_VALUES = {"Not included", "Included"}

# Runtime status values documented as reserved — must not be emitted yet.
RESERVED_MODULE_STATUS_VALUES = {
    "Initialising",
    "Available",
    "Degraded",
    "Unavailable",
    "Fault",
}

# Device-health values live today vs reserved for later module PRs.
# "Running" (not "Healthy") is the live post-warm-up value: it states only
# that the base firmware completed its startup window with no
# framework-level fault signal. "Healthy" is reserved for the future
# aggregated state where included modules report real runtime health —
# the current framework has no such signal and must not imply one.
HEALTH_VALUES_TODAY = {"Starting", "Running"}
HEALTH_VALUES_RESERVED = {"Healthy", "Degraded", "Fault", "Safe mode"}

# Shared text-sensor contract: id -> (user-facing name, enabled by default).
EXPECTED_TEXT_SENSORS = {
    "s360_device_health": ("Device Health", True),
    "s360_product_configuration": ("Product Configuration", True),
    "s360_hardware_model": ("Hardware Model", True),
    "s360_hardware_revision": ("Hardware Revision", True),
    "s360_firmware_version": ("Firmware Version", True),
    "s360_installed_capabilities": ("Installed Capabilities", True),
    "s360_firmware_channel": ("Firmware Channel", False),
    "s360_firmware_source": ("Firmware Source", False),
    "s360_capability_ids": ("Capability IDs", False),
    "s360_module_status_roomiq": ("RoomIQ Module Status", False),
    "s360_module_status_airiq": ("AirIQ Module Status", False),
    "s360_module_status_ventiq": ("VentIQ Module Status", False),
    "s360_module_status_presence": ("Presence Module Status", False),
    "s360_module_status_led": ("LED Module Status", False),
    "s360_module_status_fan_control": ("Fan Control Module Status", False),
    "s360_last_restart_reason": ("Last Restart Reason", False),
}

# Framework substitution defaults that must exist in the package itself so it
# stays safely includable by any current or future composition.
EXPECTED_SUBSTITUTION_DEFAULTS = {
    "s360_config_string",
    "s360_hardware_model",
    "s360_hardware_revision",
    "s360_firmware_version",
    "s360_firmware_channel",
    "s360_firmware_source",
    "s360_capabilities",
    "s360_capabilities_human",
    "s360_health_warmup_seconds",
    "s360_module_roomiq",
    "s360_module_airiq",
    "s360_module_ventiq",
    "s360_module_presence",
    "s360_module_led",
    "s360_module_fan_control",
}

ENTITY_PLATFORM_KEYS = (
    "sensor",
    "binary_sensor",
    "text_sensor",
    "switch",
    "number",
    "button",
    "select",
    "light",
    "fan",
)


# --- ESPHome-tag-tolerant YAML loading --------------------------------------


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


def load_yaml(path: Path) -> Dict[str, Any]:
    doc = yaml.safe_load(path.read_text())
    return doc if isinstance(doc, dict) else {}


def load_contract() -> Dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text())


def bundle_paths() -> List[Path]:
    return sorted(BUNDLES_DIR.glob("*.yaml"))


def framework_text_sensors() -> Dict[str, Dict[str, Any]]:
    """Return framework text sensors keyed by id (debug platform flattened)."""
    doc = load_yaml(FRAMEWORK_PACKAGE)
    out: Dict[str, Dict[str, Any]] = {}
    for entry in doc.get("text_sensor") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("platform") == "debug":
            nested = entry.get("reset_reason")
            if isinstance(nested, dict):
                out[str(nested.get("id"))] = nested
            continue
        out[str(entry.get("id"))] = entry
    return out


def _collect_includes(doc: Any) -> List[str]:
    """Collect local !include target strings from a packages: block."""
    packages = doc.get("packages") if isinstance(doc, dict) else None
    values: List[Any] = []
    if isinstance(packages, dict):
        values = list(packages.values())
    elif isinstance(packages, list):
        values = packages
    return [v for v in values if isinstance(v, str)]


class CompositionWalker:
    """Recursively resolve a bundle's local package includes.

    Each distinct file contributes once (ESPHome de-duplication of the empty
    shared files such as ``device_health.yaml`` is not modelled; entity-level
    duplication is what this walker feeds and ``esphome config`` remains the
    compile-time source of truth).
    """

    def __init__(self) -> None:
        self.visited: Set[Path] = set()
        # (platform, rendered name) -> list of files declaring it
        self.names: Dict[Tuple[str, str], List[Path]] = {}
        # entity id -> list of files declaring it
        self.ids: Dict[str, List[Path]] = {}
        self.substitutions: Dict[str, str] = {}

    def walk(self, path: Path) -> None:
        path = path.resolve()
        if path in self.visited or not path.is_file():
            return
        self.visited.add(path)
        doc = load_yaml(path)
        subs = doc.get("substitutions")
        if isinstance(subs, dict):
            for key, value in subs.items():
                # outermost (bundle) definition wins, matching ESPHome
                self.substitutions.setdefault(str(key), str(value))
        for platform in ENTITY_PLATFORM_KEYS:
            entries = doc.get(platform)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                self._record(platform, entry, path)
                if entry.get("platform") == "debug":
                    for nested_key in ("reset_reason", "device"):
                        nested = entry.get(nested_key)
                        if isinstance(nested, dict):
                            self._record(platform, nested, path)
        for include in _collect_includes(doc):
            self.walk((path.parent / include).resolve())

    def _record(self, platform: str, entry: Dict[str, Any], path: Path) -> None:
        entity_id = entry.get("id")
        if isinstance(entity_id, str):
            self.ids.setdefault(entity_id, []).append(path)
        if entry.get("internal") is True:
            return
        name = entry.get("name")
        if isinstance(name, str):
            rendered = self._render(name)
            self.names.setdefault((platform, rendered), []).append(path)

    def _render(self, name: str) -> str:
        def _sub(match: "re.Match[str]") -> str:
            key = match.group(1)
            return self.substitutions.get(key, "<" + key + ">")

        return re.sub(r"\$\{([A-Za-z0-9_]+)\}", _sub, name)


# --- Tests -------------------------------------------------------------------


class ContractFileTests(unittest.TestCase):
    """config/core-framework.json — the machine-readable framework contract."""

    def setUp(self) -> None:
        self.assertTrue(
            CONTRACT_PATH.is_file(),
            f"missing framework contract at {CONTRACT_PATH}",
        )
        self.contract = load_contract()

    def test_header_fields(self) -> None:
        self.assertEqual(self.contract.get("work_item"), "CORE-FRAMEWORK-001")
        self.assertIsInstance(self.contract.get("schema_version"), int)
        self.assertEqual(self.contract.get("framework_package"), FRAMEWORK_PACKAGE_REL)

    def test_capability_registry_is_stable_and_complete(self) -> None:
        capabilities = self.contract.get("capabilities") or {}
        self.assertEqual(set(capabilities), EXPECTED_CAPABILITY_IDS)
        for cap_id, cap in capabilities.items():
            self.assertRegex(cap_id, CAPABILITY_ID_RE)
            self.assertIsInstance(cap.get("display_name"), str)
            self.assertIn(cap.get("kind"), {"platform", "power", "module"})
            self.assertIsInstance(cap.get("description"), str)

    def test_module_capabilities_map_to_catalog_hardware(self) -> None:
        catalog = json.loads(HARDWARE_CATALOG.read_text())
        skus = {item["sku"]: item for item in catalog["items"]}
        capabilities = self.contract.get("capabilities") or {}
        for cap_id, cap in capabilities.items():
            sku = cap.get("hardware_sku")
            if sku is None:
                continue
            self.assertIn(
                sku,
                skus,
                f"capability {cap_id} references unknown hardware SKU {sku}",
            )

    def test_module_status_contract(self) -> None:
        status = self.contract.get("module_status") or {}
        values = status.get("values") or {}
        reserved = status.get("reserved_values") or {}
        self.assertEqual(set(values), ALLOWED_MODULE_STATUS_VALUES)
        self.assertEqual(set(reserved), RESERVED_MODULE_STATUS_VALUES)
        for meaning in list(values.values()) + list(reserved.values()):
            self.assertIsInstance(meaning, str)
            self.assertGreater(len(meaning), 10)
        # "Included" must be defined as compile-time presence, not health.
        self.assertIn("compile", values["Included"].lower())
        self.assertEqual(
            set(status.get("modules") or []), set(MODULE_STATUS_SUBSTITUTIONS)
        )

    def test_device_health_contract(self) -> None:
        health = self.contract.get("device_health") or {}
        self.assertEqual(set(health.get("values") or {}), HEALTH_VALUES_TODAY)
        self.assertEqual(
            set(health.get("reserved_values") or {}), HEALTH_VALUES_RESERVED
        )
        self.assertTrue(health.get("inputs_today"))
        self.assertTrue(health.get("reserved_inputs"))

    def test_guardrails_declare_compile_time_only(self) -> None:
        guardrails = " ".join(self.contract.get("guardrails") or []).lower()
        self.assertIn("compile-time", guardrails)
        self.assertIn("no runtime", guardrails)
        self.assertIn("release", guardrails)

    def test_capability_descriptions_claim_only_compiled_firmware(self) -> None:
        # A capability description is a statement about the FIRMWARE that is
        # compiled, never about what the PCB could carry. Components that
        # exist on the hardware but are not compiled anywhere (MICS-4514,
        # BMP581) may only be mentioned if explicitly marked as not compiled;
        # connectors are hardware possibilities and never capability evidence.
        # (PIR and SEN0609 left this list when PRESENCE-FRAMEWORK-001 compiled
        # them into the presence capability; LTR-303ALS left it when
        # S360-200-R4-HARDWARE-RECONCILIATION-001 compiled it as the RoomIQ
        # ambient-light driver — see test_presence_capability_composes_all_
        # three_sensors and tests/test_roomiq_r4_hardware_reconciliation.py.)
        capabilities = self.contract.get("capabilities") or {}
        non_compiled_components = {
            "roomiq": ["BMP581"],
        }
        for cap_id, terms in non_compiled_components.items():
            description = capabilities[cap_id]["description"]
            for term in terms:
                if term.lower() in description.lower():
                    self.assertIn(
                        "not compiled",
                        description.lower(),
                        f"{cap_id}: description names {term} (not compiled "
                        "in any configuration) without marking it as such",
                    )
        for cap_id, cap in capabilities.items():
            self.assertNotIn(
                "connector",
                str(cap.get("description", "")).lower(),
                f"{cap_id}: a connector is a hardware possibility, not "
                "compiled firmware — describe the compiled composition only",
            )

    def test_every_bundle_has_a_config_entry(self) -> None:
        configs = self.contract.get("configs") or {}
        declared_bundles = {entry.get("bundle") for entry in configs.values()}
        actual_bundles = {str(p.relative_to(REPO_ROOT)) for p in bundle_paths()}
        self.assertEqual(declared_bundles, actual_bundles)

    def test_config_capabilities_match_config_string_tokens(self) -> None:
        configs = self.contract.get("configs") or {}
        for config_string, entry in configs.items():
            caps = set(entry.get("capabilities") or [])
            expected = {"core"}
            for token in config_string.split("-"):
                expected |= TOKEN_CAPABILITIES.get(token, set())
            self.assertEqual(
                caps,
                expected,
                f"{config_string}: capabilities {sorted(caps)} do not match "
                f"config-string tokens (expected {sorted(expected)})",
            )

    def test_config_capabilities_match_product_catalog_modules(self) -> None:
        catalog = json.loads(PRODUCT_CATALOG.read_text())
        by_config = {
            p.get("config_string"): p
            for p in catalog.get("products", [])
            if p.get("config_string")
        }
        configs = self.contract.get("configs") or {}
        for config_string, entry in configs.items():
            product = by_config.get(config_string)
            self.assertIsNotNone(
                product, f"{config_string} missing from product catalog"
            )
            modules = product.get("modules") or {}
            caps = set(entry.get("capabilities") or [])
            self.assertEqual(modules.get("air_quality") == "VentIQ", "ventiq" in caps)
            self.assertEqual(modules.get("air_quality") == "AirIQ", "airiq" in caps)
            self.assertEqual(modules.get("room_sense") == "RoomIQ", "roomiq" in caps)
            self.assertEqual(modules.get("led") == "LED", "led" in caps)
            fan = modules.get("fan", "none")
            fan_caps = {c for c in caps if c.startswith("fan_")}
            if fan == "none":
                self.assertEqual(fan_caps, set())
            else:
                self.assertEqual(fan_caps, {"fan_" + fan[3:].lower()})
            power = modules.get("power")
            self.assertEqual(power == "POE", "power_poe" in caps)
            self.assertEqual(power == "USB", "power_usb" in caps)


class FrameworkPackageTests(unittest.TestCase):
    """packages/base/device_framework.yaml — the reusable framework package."""

    def setUp(self) -> None:
        self.assertTrue(
            FRAMEWORK_PACKAGE.is_file(),
            f"missing framework package at {FRAMEWORK_PACKAGE}",
        )
        self.doc = load_yaml(FRAMEWORK_PACKAGE)
        self.raw = FRAMEWORK_PACKAGE.read_text()
        self.sensors = framework_text_sensors()

    def test_substitution_defaults_present(self) -> None:
        subs = self.doc.get("substitutions") or {}
        missing = EXPECTED_SUBSTITUTION_DEFAULTS - set(subs)
        self.assertEqual(missing, set(), f"missing defaults: {sorted(missing)}")

    def test_module_defaults_are_not_included(self) -> None:
        subs = self.doc.get("substitutions") or {}
        for sub_key in MODULE_STATUS_SUBSTITUTIONS.values():
            self.assertEqual(
                subs.get(sub_key),
                "Not included",
                f"{sub_key} must default to 'Not included' so an absent "
                "module never reads as present or faulted",
            )

    def test_expected_entities_present_with_stable_ids(self) -> None:
        self.assertEqual(set(self.sensors), set(EXPECTED_TEXT_SENSORS))

    def test_names_and_enabled_defaults(self) -> None:
        for entity_id, (name, enabled) in EXPECTED_TEXT_SENSORS.items():
            entry = self.sensors[entity_id]
            self.assertEqual(entry.get("name"), name, entity_id)
            disabled = bool(entry.get("disabled_by_default", False))
            self.assertEqual(
                disabled,
                not enabled,
                f"{entity_id}: disabled_by_default must be {not enabled}",
            )

    def test_all_entities_are_diagnostic(self) -> None:
        for entity_id, entry in self.sensors.items():
            self.assertEqual(
                entry.get("entity_category"),
                "diagnostic",
                f"{entity_id} must be entity_category: diagnostic",
            )

    def test_names_do_not_duplicate_device_name(self) -> None:
        for entity_id, entry in self.sensors.items():
            name = entry.get("name", "")
            self.assertNotIn("${friendly_name}", name, entity_id)
            self.assertNotIn("${device_name}", name, entity_id)
            self.assertNotIn("$friendly_name", name, entity_id)

    def test_names_are_not_raw_ids(self) -> None:
        for entity_id, entry in self.sensors.items():
            name = entry.get("name", "")
            self.assertNotIn("_", name, f"{entity_id} name looks like a raw id")
            self.assertFalse(
                name.islower(), f"{entity_id} name is not title-styled: {name}"
            )

    def test_no_measurement_metadata_misuse(self) -> None:
        # Text sensors carry no device_class / state_class / units.
        for entity_id, entry in self.sensors.items():
            for forbidden in ("device_class", "state_class", "unit_of_measurement"):
                self.assertNotIn(forbidden, entry, entity_id)

    def test_no_secret_material(self) -> None:
        self.assertNotIn("!secret", self.raw)
        lowered = self.raw.lower()
        for needle in ("password", "api_encryption", "token"):
            self.assertNotIn(needle, lowered)

    def _emission_surface(self) -> str:
        """Everything the framework can actually publish: substitution
        defaults plus entity names and lambda bodies (comments excluded)."""
        parts: List[str] = []
        subs = self.doc.get("substitutions") or {}
        parts.extend(str(v) for v in subs.values())
        for entry in self.sensors.values():
            parts.append(str(entry.get("name", "")))
            parts.append(str(entry.get("lambda", "")))
        return "\n".join(parts)

    def test_health_entity_uses_documented_values_only(self) -> None:
        health = self.sensors["s360_device_health"]
        lambda_body = str(health.get("lambda", ""))
        for value in HEALTH_VALUES_TODAY:
            self.assertIn(value, lambda_body)
        # Reserved runtime values must not be fabricated by the framework:
        # nothing the framework can publish (substitution defaults, entity
        # names, lambda bodies) may carry them. Comments documenting the
        # reservation are allowed.
        emission = self._emission_surface()
        for value in RESERVED_MODULE_STATUS_VALUES | HEALTH_VALUES_RESERVED:
            self.assertNotIn(
                value,
                emission,
                f"framework must not emit reserved runtime value {value!r} "
                "before a real signal exists",
            )
        self.assertIn("${s360_health_warmup_seconds}", lambda_body)

    def test_module_status_entities_reflect_substitutions(self) -> None:
        for module, sub_key in MODULE_STATUS_SUBSTITUTIONS.items():
            entry = self.sensors["s360_module_status_" + module]
            self.assertIn("${" + sub_key + "}", str(entry.get("lambda", "")))

    def test_capability_entities_reflect_substitutions(self) -> None:
        self.assertIn(
            "${s360_capabilities_human}",
            str(self.sensors["s360_installed_capabilities"].get("lambda", "")),
        )
        self.assertIn(
            "${s360_capabilities}",
            str(self.sensors["s360_capability_ids"].get("lambda", "")),
        )

    def test_no_runtime_detection_claim_in_static_entities(self) -> None:
        # Compile-time facts must never be labelled as runtime detection in
        # anything the framework publishes (names / lambdas / defaults).
        lowered = self._emission_surface().lower()
        self.assertNotIn("detected", lowered)
        self.assertNotIn("autodetect", lowered)


class BundleWiringTests(unittest.TestCase):
    """Every bundle declares its compile-time capabilities and includes the
    framework package exactly once."""

    def setUp(self) -> None:
        self.assertTrue(CONTRACT_PATH.is_file(), "missing framework contract")
        self.contract = load_contract()
        self.configs: Dict[str, Dict[str, Any]] = self.contract.get("configs") or {}
        self.capabilities: Dict[str, Dict[str, Any]] = (
            self.contract.get("capabilities") or {}
        )
        self.assertTrue(self.configs, "contract declares no configs")

    def _bundle_doc(self, entry: Dict[str, Any]) -> Tuple[Path, Dict[str, Any]]:
        bundle = REPO_ROOT / entry["bundle"]
        self.assertTrue(bundle.is_file(), f"missing bundle {bundle}")
        return bundle, load_yaml(bundle)

    def test_bundles_include_framework_exactly_once(self) -> None:
        for config_string, entry in self.configs.items():
            bundle, _ = self._bundle_doc(entry)
            occurrences = bundle.read_text().count(
                "!include ../../packages/base/device_framework.yaml"
            )
            expected = 1 if entry.get("framework_included", True) else 0
            self.assertEqual(
                occurrences,
                expected,
                f"{config_string}: bundle must include the framework package "
                f"exactly {expected} time(s) (found {occurrences})",
            )

    def test_deferred_configs_document_why(self) -> None:
        # A config may only opt out of the framework with an explicit,
        # documented deferral (currently: the FanPWM native-compile
        # identity gate, tests/test_pwm_product_readiness.py).
        deferred = {
            cs: entry
            for cs, entry in self.configs.items()
            if not entry.get("framework_included", True)
        }
        self.assertEqual(set(deferred), {"Ceiling-POE-FanPWM"})
        for config_string, entry in deferred.items():
            reason = entry.get("deferral_reason", "")
            self.assertGreater(
                len(reason),
                40,
                f"{config_string}: deferral requires a documented reason",
            )
            self.assertIn("identical", reason.lower())

    def test_bundle_substitutions_match_contract(self) -> None:
        for config_string, entry in self.configs.items():
            if not entry.get("framework_included", True):
                continue
            _, doc = self._bundle_doc(entry)
            subs = doc.get("substitutions") or {}
            caps: List[str] = entry.get("capabilities") or []
            self.assertEqual(subs.get("s360_config_string"), config_string)
            self.assertEqual(subs.get("s360_capabilities"), ",".join(caps))
            human = ", ".join(self.capabilities[c]["display_name"] for c in caps)
            self.assertEqual(subs.get("s360_capabilities_human"), human)
            self.assertEqual(
                subs.get("s360_hardware_model"), entry.get("hardware_model")
            )
            self.assertEqual(
                subs.get("s360_hardware_revision"),
                entry.get("hardware_revision"),
            )

    def test_bundle_module_flags_match_capabilities(self) -> None:
        for config_string, entry in self.configs.items():
            if not entry.get("framework_included", True):
                continue
            _, doc = self._bundle_doc(entry)
            subs = doc.get("substitutions") or {}
            caps = set(entry.get("capabilities") or [])
            included_modules = {
                CAPABILITY_TO_MODULE[c] for c in caps if c in CAPABILITY_TO_MODULE
            }
            for module, sub_key in MODULE_STATUS_SUBSTITUTIONS.items():
                value = subs.get(sub_key, "Not included")
                self.assertIn(
                    value,
                    ALLOWED_MODULE_STATUS_VALUES,
                    f"{config_string}: {sub_key}={value!r} is outside the "
                    f"compile-time status set",
                )
                expected = "Included" if module in included_modules else "Not included"
                self.assertEqual(
                    value,
                    expected,
                    f"{config_string}: {sub_key} must be {expected!r}",
                )

    def test_absent_module_is_never_a_fault(self) -> None:
        # An optional module that is not part of the composition must read
        # exactly 'Not included' — never Fault / Unavailable / anything else.
        for config_string, entry in self.configs.items():
            _, doc = self._bundle_doc(entry)
            subs = doc.get("substitutions") or {}
            for sub_key in MODULE_STATUS_SUBSTITUTIONS.values():
                value = subs.get(sub_key)
                if value is None:
                    continue
                self.assertNotIn(value, RESERVED_MODULE_STATUS_VALUES)

    def test_hardware_identity_is_catalog_backed(self) -> None:
        catalog = json.loads(HARDWARE_CATALOG.read_text())
        by_sku = {item["sku"]: item for item in catalog["items"]}
        for config_string, entry in self.configs.items():
            model = entry.get("hardware_model")
            self.assertIn(
                model,
                by_sku,
                f"{config_string}: hardware_model {model!r} not in catalog",
            )
            self.assertEqual(entry.get("hardware_revision"), by_sku[model]["rev"])


class CapabilityCompositionEvidenceTests(unittest.TestCase):
    """A declared capability means the backing firmware package is actually
    compiled into that configuration — never that the PCB supports it, a
    connector exists, or a module might be fitted later.

    Evidence = the capability's authoritative package file resolves in the
    bundle's composition (board package or its preserved legacy alias). Both
    directions are enforced: declared => compiled, and compiled => declared.
    """

    # capability id -> filename fragments that prove the firmware is composed
    CAPABILITY_EVIDENCE = {
        "roomiq": ("s360-200-roomiq-climate",),
        "presence": ("s360-200-roomiq-radar",),
        "airiq": ("s360-210-airiq", "airiq_ceiling"),
        "ventiq": ("s360-211-ventiq", "airiq_bathroom_base"),
        "led": ("s360-300-led", "led_ring", "halo"),
        "fan_relay": ("fan_relay",),
        "fan_pwm": ("fan_pwm",),
        "fan_dac": ("fan_dac", "fan_gp8403"),
        "fan_triac": ("fan_triac", "triac"),
        "power_poe": ("s360-410-poe-psu", "power_poe"),
        "power_usb": ("power_usb",),
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_contract()
        cls.resolved: Dict[str, str] = {}
        for config_string, entry in cls.contract.get("configs", {}).items():
            walker = CompositionWalker()
            walker.walk(REPO_ROOT / entry["bundle"])
            cls.resolved[config_string] = " ".join(str(p) for p in walker.visited)

    def test_declared_capability_has_compiled_evidence(self) -> None:
        for config_string, entry in self.contract["configs"].items():
            files = self.resolved[config_string]
            for cap in entry.get("capabilities") or []:
                if cap == "core":
                    continue
                fragments = self.CAPABILITY_EVIDENCE[cap]
                self.assertTrue(
                    any(f in files for f in fragments),
                    f"{config_string}: declares capability {cap!r} but none "
                    f"of its backing packages {fragments} resolve in the "
                    "bundle composition — a capability must mean the "
                    "firmware is compiled in, not that hardware could be "
                    "fitted",
                )

    def test_compiled_firmware_is_declared_as_capability(self) -> None:
        for config_string, entry in self.contract["configs"].items():
            files = self.resolved[config_string]
            declared = set(entry.get("capabilities") or [])
            for cap, fragments in self.CAPABILITY_EVIDENCE.items():
                if any(f in files for f in fragments):
                    self.assertIn(
                        cap,
                        declared,
                        f"{config_string}: composes {cap!r} firmware "
                        f"({fragments}) but does not declare the capability",
                    )

    def test_presence_capability_composes_all_three_sensors(self) -> None:
        # PRESENCE-FRAMEWORK-001 (deliberate update of the former
        # ld2450-only guard): the presence capability is the tri-sensor
        # composition — LD2450 radar half + PIR adapter + SEN0609 adapter +
        # the fusion framework. The legacy dual-definition C4001 package
        # stays out of every composition (its GPIO map predates
        # CORE-ABSTRACT-BUS-001C and conflicts with the schematic).
        for config_string, entry in self.contract["configs"].items():
            files = self.resolved[config_string]
            self.assertNotIn("presence_dfrobot_c4001", files, config_string)
            if "presence" not in (entry.get("capabilities") or []):
                continue
            for fragment in (
                "s360-200-roomiq-radar",
                "s360-200-roomiq-pir",
                "s360-200-roomiq-sen0609",
                "presence_framework",
            ):
                self.assertIn(
                    fragment,
                    files,
                    f"{config_string}: presence capability requires the "
                    f"tri-sensor composition ({fragment} missing)",
                )


class IsolationTests(unittest.TestCase):
    """The framework is composed by bundles only — compile-only skeletons,
    the bench harness, board packages and feature profiles stay isolated."""

    def _referencing_files(self, root: Path) -> List[Path]:
        hits: List[Path] = []
        for path in sorted(root.rglob("*.yaml")):
            if "device_framework" in path.read_text():
                hits.append(path)
        return hits

    def test_compile_only_skeletons_do_not_include_framework(self) -> None:
        self.assertEqual(self._referencing_files(COMPILE_ONLY_DIR), [])

    def test_bench_harness_does_not_include_framework(self) -> None:
        self.assertEqual(self._referencing_files(REPO_ROOT / "tests"), [])

    def test_only_bundles_compose_the_framework(self) -> None:
        for subdir in ("boards", "features", "hardware", "expansions"):
            self.assertEqual(
                self._referencing_files(REPO_ROOT / "packages" / subdir),
                [],
                f"packages/{subdir} must not include the framework package "
                "(bundles compose it exactly once)",
            )


class CompositionRegressionTests(unittest.TestCase):
    """No duplicate entity names or IDs across resolved bundle compositions,
    and the shared entities are actually part of every bundle."""

    def _walk(self, bundle: Path) -> CompositionWalker:
        walker = CompositionWalker()
        walker.walk(bundle)
        return walker

    def test_no_duplicate_entity_names_per_bundle(self) -> None:
        for bundle in bundle_paths():
            walker = self._walk(bundle)
            duplicates = {
                key: [str(p.relative_to(REPO_ROOT)) for p in paths]
                for key, paths in walker.names.items()
                if len(paths) > 1
            }
            self.assertEqual(duplicates, {}, f"duplicate entity names in {bundle.name}")

    def test_no_duplicate_entity_ids_per_bundle(self) -> None:
        for bundle in bundle_paths():
            walker = self._walk(bundle)
            duplicates = {
                key: [str(p.relative_to(REPO_ROOT)) for p in paths]
                for key, paths in walker.ids.items()
                if len(paths) > 1
            }
            self.assertEqual(duplicates, {}, f"duplicate entity ids in {bundle.name}")

    def test_framework_entities_reach_every_bundle(self) -> None:
        contract = load_contract()
        deferred_bundles = {
            (REPO_ROOT / entry["bundle"]).resolve()
            for entry in (contract.get("configs") or {}).values()
            if not entry.get("framework_included", True)
        }
        for bundle in bundle_paths():
            if bundle.resolve() in deferred_bundles:
                continue
            walker = self._walk(bundle)
            resolved = {p for p in walker.visited}
            self.assertIn(
                FRAMEWORK_PACKAGE.resolve(),
                resolved,
                f"{bundle.name} does not resolve the framework package",
            )
            for entity_id in EXPECTED_TEXT_SENSORS:
                self.assertIn(entity_id, walker.ids, bundle.name)

    def test_release_declarations_unchanged_shape(self) -> None:
        # The framework is firmware-composition only: the release matrix
        # keeps exactly its declared builds and the framework adds none.
        builds = json.loads((REPO_ROOT / "config" / "webflash-builds.json").read_text())
        rows = builds.get("builds") or []
        self.assertEqual(len(rows), 14)
        for row in rows:
            self.assertNotIn("framework", json.dumps(row).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

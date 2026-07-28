#!/usr/bin/env python3
"""STATIC-DIAGNOSTIC-PUBLISH-001 — static diagnostics must publish at boot.

The defect
----------
Every Sense360 identity / capability / board-SKU diagnostic is a template
``text_sensor`` whose value is a compile-time constant, declared as::

    - platform: template
      name: "Product Configuration"
      update_interval: never
      lambda: |-
        return {"${s360_config_string}"};

``update_interval: never`` means ESPHome never polls the component, so the
lambda is never evaluated and no state is ever published. Home Assistant
therefore shows the entity as **Unknown** for the whole life of the device,
even though the value is baked into the firmware at compile time.

The contract pinned here
------------------------
* A template text sensor that is never polled AND carries a ``lambda`` is a
  **static** value: it must be published exactly once at boot via
  ``component.update`` from an ``esphome: on_boot:`` hook **in the same file
  that declares it** (so a partial composition can never lose the publish).
* The publication runs at boot priority ``500``
  (:data:`STATIC_PUBLISH_BOOT_PRIORITY`) — after the text-sensor components
  are set up (ESPHome ``setup_priority::HARDWARE`` = 800) and *before* every
  runtime framework boot hook (priority 250) and before any ``interval:``
  tick (which only runs once ``App.setup()`` has completed). A runtime owner
  therefore always wins over the compile-time seed value, and the seed value
  is never re-applied afterwards.
* Static diagnostics keep ``update_interval: never``: an immutable string is
  published once, never polled on a timer.
* A template text sensor that is never polled and carries **no** lambda is
  **action-published** — some script/automation owns ``publish_state`` for
  it. Those are already correct and must not be converted into polling
  compile-time lambdas.
* Generic board-identity substitutions (``module_sku`` / ``module_variant``)
  are forbidden: ESPHome merges every package's ``substitutions:`` into ONE
  flat namespace where the later-declared package wins, so AirIQ, VentIQ and
  RoomIQ sharing ``module_sku`` made a combined composition report one
  board's SKU on another board's entity. Board identity uses board-specific
  substitution names.
* ``esphome: on_boot:`` is written in list form in every package.
  ``esphome.config_helpers.merge_config`` replaces (rather than merges) a
  mapping with a list, so a map-form ``on_boot:`` in one package silently
  deletes every other package's boot hooks during package merging.

Uses Python's stdlib unittest (repo convention). Run with::

    python3 tests/test_static_diagnostic_publish.py

or::

    python3 -m unittest tests.test_static_diagnostic_publish -v
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

PACKAGES_DIR = REPO_ROOT / "packages"
PRODUCTS_DIR = REPO_ROOT / "products"
DEVICE_FRAMEWORK = REPO_ROOT / "packages" / "base" / "device_framework.yaml"

# The single documented boot priority for publishing compile-time constants.
# 800 (setup_priority::HARDWARE) is when template text sensors are set up; the
# runtime frameworks seed their own state from on_boot priority 250 and keep
# it current from `interval:` ticks that only run after setup completes.
STATIC_PUBLISH_BOOT_PRIORITY = 500

# The highest boot priority any runtime module-status owner uses. The static
# seed must run strictly earlier (i.e. at a numerically HIGHER priority) so a
# runtime value is never overwritten by the compile-time one.
RUNTIME_FRAMEWORK_BOOT_PRIORITY = 250

# --- pinned customer-facing surface ----------------------------------------

# Shared device-framework identity / capability entities: id -> (name, lambda
# substitution it must render). These names and ids are customer-facing and
# are pinned so this work item cannot rename them.
IDENTITY_ENTITIES: Dict[str, Tuple[str, str]] = {
    "s360_product_configuration": ("Product Configuration", "s360_config_string"),
    "s360_hardware_model": ("Hardware Model", "s360_hardware_model"),
    "s360_hardware_revision": ("Hardware Revision", "s360_hardware_revision"),
    "s360_firmware_version": ("Firmware Version", "s360_firmware_version"),
    "s360_firmware_channel": ("Firmware Channel", "s360_firmware_channel"),
    "s360_firmware_source": ("Firmware Source", "s360_firmware_source"),
    "s360_installed_capabilities": (
        "Installed Capabilities",
        "s360_capabilities_human",
    ),
    "s360_capability_ids": ("Capability IDs", "s360_capabilities"),
}

# Module-status entities: id -> (name, substitution, runtime owner or None).
MODULE_STATUS_ENTITIES: Dict[str, Tuple[str, str, Optional[str]]] = {
    "s360_module_status_roomiq": (
        "RoomIQ Module Status",
        "s360_module_roomiq",
        "packages/features/roomiq_framework.yaml",
    ),
    "s360_module_status_airiq": (
        "AirIQ Module Status",
        "s360_module_airiq",
        "packages/features/airiq_framework.yaml",
    ),
    "s360_module_status_ventiq": (
        "VentIQ Module Status",
        "s360_module_ventiq",
        "packages/features/ventiq_framework.yaml",
    ),
    "s360_module_status_presence": (
        "Presence Module Status",
        "s360_module_presence",
        "packages/features/presence_framework.yaml",
    ),
    "s360_module_status_led": ("LED Module Status", "s360_module_led", None),
    "s360_module_status_fan_control": (
        "Fan Control Module Status",
        "s360_module_fan_control",
        None,
    ),
}

# Board identity entities: file -> (id, customer-facing name, board-specific
# substitution key, its declared value). Names are pinned; the substitution
# names are board-specific so a combined composition cannot cross-contaminate.
#
# SENSE360-CANONICALISATION-001 PR 05: the declared VALUES are now the
# canonical board SKUs from config/hardware-catalog.json. They were legacy
# variant terminology (S360-LED-C, S360-LED-V-C, S360-PRES-C, S360-AIR-C,
# S360-BATH-B) which the SOT identity schema does not admit as board SKUs
# (^S360-[0-9]{3}$). Updated in the same commit as the substitutions they
# govern, so no window exists in which the guard does not cover them.
BOARD_SKU_ENTITIES: Dict[str, Tuple[str, str, str, str]] = {
    "packages/boards/s360-300-led.yaml": (
        "s360_led_ring_sku",
        "${friendly_name} LED Ring SKU",
        "led_ring_sku",
        "S360-300",
    ),
    # s360-300-led-mic-ceiling.yaml was deleted under PR 07 (zero-alias):
    # the undocumented led-mic pair failed the owner evidence test of
    # 2026-07-28 and both halves were internal and removable
    # (tests/test_zero_alias.py pins the deletion).
    "packages/boards/s360-200-roomiq-radar.yaml": (
        "s360_presence_module_sku",
        "${friendly_name} Presence Module SKU",
        "roomiq_presence_module_sku",
        "S360-200",
    ),
    "packages/boards/s360-210-airiq.yaml": (
        "s360_airiq_module_sku",
        "${friendly_name} AirIQ Module SKU",
        "airiq_module_sku",
        "S360-210",
    ),
    "packages/boards/s360-211-ventiq.yaml": (
        "s360_ventiq_module_sku",
        "${friendly_name} AirIQ Module SKU",
        "ventiq_module_sku",
        "S360-211",
    ),
}

# Substitution names that must never be used again for board identity: they
# are generic, so two board packages composed together collide in ESPHome's
# single flat substitution namespace.
BANNED_GENERIC_IDENTITY_SUBSTITUTIONS = ("module_sku", "module_variant")

# Product-identification entities every bundle / product / compile-only
# skeleton declares (ids added by this work item; names untouched).
PRODUCT_IDENTITY_IDS = (
    "s360_product_sku",
    "s360_product_firmware_version",
    "s360_product_config_string",
)


# --- ESPHome-tag-tolerant YAML loading (repo convention) --------------------


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


def _is_repository_yaml(path: Path) -> bool:
    """Skip generated build trees (``.esphome/``) and local secrets."""
    if path.name == "secrets.yaml":
        return False
    return not any(part.startswith(".") for part in path.relative_to(REPO_ROOT).parts)


def yaml_files() -> List[Path]:
    """Every composable YAML file: packages, bundles, products, skeletons."""
    found: List[Path] = []
    for base in (PACKAGES_DIR, PRODUCTS_DIR):
        found.extend(p for p in base.rglob("*.yaml") if _is_repository_yaml(p))
    return sorted(found)


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


# --- text-sensor classification --------------------------------------------


def never_polled_text_sensors(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = doc.get("text_sensor")
    if not isinstance(entries, list):
        return []
    return [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("platform") == "template"
        and str(entry.get("update_interval")) == "never"
    ]


def static_text_sensors(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Never-polled template text sensors whose value comes from a lambda."""
    return [e for e in never_polled_text_sensors(doc) if "lambda" in e]


def action_published_text_sensors(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Never-polled template text sensors with no lambda (script-published)."""
    return [e for e in never_polled_text_sensors(doc) if "lambda" not in e]


def on_boot_entries(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    esphome = doc.get("esphome")
    if not isinstance(esphome, dict):
        return []
    hooks = esphome.get("on_boot")
    if isinstance(hooks, dict):  # map form (merge hazard — asserted below)
        return [hooks]
    if isinstance(hooks, list):
        return [h for h in hooks if isinstance(h, dict)]
    return []


def _iter_actions(node: Any) -> Iterable[Any]:
    if isinstance(node, dict):
        for value in node.values():
            yield from _iter_actions(value)
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from _iter_actions(item)


def boot_published_ids(doc: Dict[str, Any]) -> List[Tuple[str, Any]]:
    """(component id, boot priority) for every ``component.update`` at boot."""
    published: List[Tuple[str, Any]] = []
    for hook in on_boot_entries(doc):
        priority = hook.get("priority")
        for action in _iter_actions(hook.get("then")):
            if isinstance(action, dict) and "component.update" in action:
                published.append((str(action["component.update"]), priority))
    return published


# --- ESPHome substitution resolution ---------------------------------------


def _package_paths(doc: Dict[str, Any], base_dir: Path) -> List[Path]:
    """Local ``!include``d package paths, in declaration order."""
    packages = doc.get("packages")
    if isinstance(packages, dict):
        values = list(packages.values())
    elif isinstance(packages, list):
        values = list(packages)
    else:
        return []
    paths: List[Path] = []
    for value in values:
        if not isinstance(value, str):
            continue  # remote package dicts carry no local path
        candidate = (base_dir / value).resolve()
        if candidate.is_file():
            paths.append(candidate)
    return paths


def resolve_substitutions(path: Path) -> Dict[str, str]:
    """Resolve a composition's substitutions exactly the way ESPHome does.

    ``esphome/components/packages`` walks packages **highest priority first**
    (later-declared before earlier-declared, depth-first into nested
    packages) and skips any substitution key already claimed, so the FIRST
    claimant in that walk wins. The consuming config's own top-level
    substitutions are claimed before any package's.
    """
    resolved: Dict[str, str] = {}
    visited: set = set()

    def claim(subs: Any) -> None:
        if not isinstance(subs, dict):
            return
        for key, value in subs.items():
            resolved.setdefault(str(key), str(value))

    def walk(current: Path) -> None:
        if current in visited:
            return
        visited.add(current)
        doc = load_yaml(current)
        claim(doc.get("substitutions"))
        for package in reversed(_package_paths(doc, current.parent)):
            walk(package)

    doc = load_yaml(path)
    claim(doc.get("substitutions"))
    for package in reversed(_package_paths(doc, path.parent)):
        walk(package)

    # Expand substitutions that reference other substitutions (one pass is
    # enough for this repository's single-level references).
    for key, value in list(resolved.items()):
        resolved[key] = expand(value, resolved)
    return resolved


SUBSTITUTION_RE = re.compile(r"\$\{([a-zA-Z0-9_]+)\}")


def expand(text: str, subs: Dict[str, str]) -> str:
    return SUBSTITUTION_RE.sub(lambda m: subs.get(m.group(1), m.group(0)), text)


def composed_files(path: Path) -> List[Path]:
    """Every local YAML file composed by ``path`` (itself included)."""
    seen: List[Path] = []

    def walk(current: Path) -> None:
        if current in seen:
            return
        seen.append(current)
        doc = load_yaml(current)
        for package in _package_paths(doc, current.parent):
            walk(package)

    walk(path.resolve())
    return seen


def product_entry_points() -> List[Path]:
    """Customer-facing product YAML (shims, bundles, standalone products)."""
    return sorted(
        p
        for p in PRODUCTS_DIR.rglob("*.yaml")
        if _is_repository_yaml(p) and "secrets" not in p.name
    )


# --- static publication contract -------------------------------------------


class StaticPublicationContractTests(unittest.TestCase):
    """Every compile-time text sensor has exactly one boot publication."""

    def test_every_static_text_sensor_declares_a_stable_id(self) -> None:
        missing: List[str] = []
        for path in yaml_files():
            for entry in static_text_sensors(load_yaml(path)):
                if not entry.get("id"):
                    missing.append(f"{rel(path)}: {entry.get('name')}")
        self.assertEqual(
            [],
            missing,
            "Static compile-time text sensors need a stable internal id so "
            "they can be published once at boot:\n  " + "\n  ".join(missing),
        )

    def test_every_static_text_sensor_is_published_once_at_boot(self) -> None:
        missing: List[str] = []
        duplicated: List[str] = []
        for path in yaml_files():
            doc = load_yaml(path)
            statics = static_text_sensors(doc)
            if not statics:
                continue
            published = [pid for pid, _ in boot_published_ids(doc)]
            for entry in statics:
                entry_id = entry.get("id")
                if not entry_id:
                    continue  # covered by the id test above
                count = published.count(entry_id)
                if count == 0:
                    missing.append(f"{rel(path)}: {entry_id}")
                elif count > 1:
                    duplicated.append(f"{rel(path)}: {entry_id} x{count}")
        self.assertEqual(
            [],
            missing,
            "A lambda-based text sensor with `update_interval: never` is "
            "never evaluated, so it stays Unknown forever. Publish it once "
            "at boot with `component.update` in the SAME file:\n  "
            + "\n  ".join(missing),
        )
        self.assertEqual(
            [],
            duplicated,
            "A static value must be published exactly once:\n  "
            + "\n  ".join(duplicated),
        )

    def test_static_publication_uses_the_documented_boot_priority(self) -> None:
        wrong: List[str] = []
        for path in yaml_files():
            doc = load_yaml(path)
            static_ids = {e.get("id") for e in static_text_sensors(doc)}
            for entry_id, priority in boot_published_ids(doc):
                if entry_id not in static_ids:
                    continue
                if priority != STATIC_PUBLISH_BOOT_PRIORITY:
                    wrong.append(f"{rel(path)}: {entry_id} at priority {priority}")
        self.assertEqual(
            [],
            wrong,
            f"Static diagnostics publish at boot priority "
            f"{STATIC_PUBLISH_BOOT_PRIORITY}: after text-sensor setup (800) "
            f"and before every runtime framework hook "
            f"({RUNTIME_FRAMEWORK_BOOT_PRIORITY}):\n  " + "\n  ".join(wrong),
        )

    def test_static_diagnostics_are_never_polled_on_a_timer(self) -> None:
        """Immutable strings are published once, not re-rendered forever."""
        polled: List[str] = []
        framework = load_yaml(DEVICE_FRAMEWORK)
        entries = framework.get("text_sensor", [])
        pinned = set(IDENTITY_ENTITIES) | set(MODULE_STATUS_ENTITIES)
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("id") not in pinned:
                continue
            if str(entry.get("update_interval")) != "never":
                polled.append(f"{entry.get('id')}: {entry.get('update_interval')}")
        self.assertEqual(
            [],
            polled,
            "Compile-time identity/module-status entities must keep "
            "`update_interval: never` — a periodic identity lambda would "
            "overwrite runtime module status:\n  " + "\n  ".join(polled),
        )

    def test_action_published_text_sensors_keep_their_runtime_owner(self) -> None:
        """Lambda-less never-polled sensors already have a publish owner."""
        corpus = "\n".join(p.read_text() for p in yaml_files())
        orphaned: List[str] = []
        for path in yaml_files():
            for entry in action_published_text_sensors(load_yaml(path)):
                entry_id = entry.get("id")
                if not entry_id:
                    orphaned.append(f"{rel(path)}: unnamed action-published sensor")
                elif (
                    f"id({entry_id}).publish_state" not in corpus
                    # A sense360 domain component bound by id is a publish
                    # owner too (SENSE360-CANONICALISATION-001 PR 09..11:
                    # e.g. `legacy_air_quality_id: air_quality_state` feeds
                    # the entity from component glue).
                    and not re.search(rf"\w+_id: {re.escape(entry_id)}\b", corpus)
                ):
                    orphaned.append(f"{rel(path)}: {entry_id}")
        self.assertEqual(
            [],
            orphaned,
            "Action-published text sensors must have a publish_state owner "
            "(and must NOT be converted into polling compile-time "
            "lambdas):\n  " + "\n  ".join(orphaned),
        )

    def test_package_on_boot_blocks_use_list_form(self) -> None:
        """Map-form on_boot silently deletes other packages' boot hooks.

        ``esphome.config_helpers.merge_config`` returns the new value
        outright when a mapping meets a list, so one map-form ``on_boot:``
        drops every boot hook merged so far (or is itself dropped).
        """
        map_form: List[str] = []
        for path in yaml_files():
            esphome = load_yaml(path).get("esphome")
            if isinstance(esphome, dict) and isinstance(esphome.get("on_boot"), dict):
                map_form.append(rel(path))
        self.assertEqual(
            [],
            map_form,
            "`esphome: on_boot:` must be a list (`- priority: ...`) so "
            "package merging concatenates boot hooks instead of replacing "
            "them:\n  " + "\n  ".join(map_form),
        )


# --- identity / capability surface -----------------------------------------


class IdentityEntityTests(unittest.TestCase):
    """The seven reported entities publish their declared substitutions."""

    def setUp(self) -> None:
        self.doc = load_yaml(DEVICE_FRAMEWORK)
        self.by_id = {
            e["id"]: e
            for e in self.doc.get("text_sensor", [])
            if isinstance(e, dict) and e.get("id")
        }
        self.published = {pid for pid, _ in boot_published_ids(self.doc)}

    def test_identity_entities_render_their_declared_substitution(self) -> None:
        for entry_id, (name, substitution) in IDENTITY_ENTITIES.items():
            with self.subTest(entity=entry_id):
                entry = self.by_id.get(entry_id)
                self.assertIsNotNone(entry, f"{entry_id} missing from the framework")
                self.assertEqual(name, entry.get("name"))
                self.assertIn(
                    "${" + substitution + "}",
                    str(entry.get("lambda", "")),
                    f"{entry_id} must render ${{{substitution}}}",
                )

    def test_identity_entities_publish_at_boot(self) -> None:
        for entry_id in IDENTITY_ENTITIES:
            with self.subTest(entity=entry_id):
                self.assertIn(
                    entry_id,
                    self.published,
                    f"{entry_id} is never published and stays Unknown",
                )

    def test_firmware_version_defaults_to_the_declared_device_version(self) -> None:
        subs = self.doc.get("substitutions", {})
        self.assertEqual("${device_version}", subs.get("s360_firmware_version"))

    def test_capability_human_text_and_capability_ids_both_publish(self) -> None:
        self.assertIn("s360_installed_capabilities", self.published)
        self.assertIn("s360_capability_ids", self.published)

    def test_module_status_entities_publish_their_compile_time_seed(self) -> None:
        for entry_id, (name, substitution, _owner) in MODULE_STATUS_ENTITIES.items():
            with self.subTest(entity=entry_id):
                entry = self.by_id.get(entry_id)
                self.assertIsNotNone(entry)
                self.assertEqual(name, entry.get("name"))
                self.assertIn("${" + substitution + "}", str(entry.get("lambda", "")))
                self.assertIn(entry_id, self.published)


class BoardSkuEntityTests(unittest.TestCase):
    """LED Ring SKU / Presence Module SKU / air-quality SKU publish."""

    def test_board_sku_entities_have_ids_names_and_boot_publication(self) -> None:
        for relpath, (
            entry_id,
            name,
            substitution,
            value,
        ) in BOARD_SKU_ENTITIES.items():
            with self.subTest(package=relpath):
                path = REPO_ROOT / relpath
                doc = load_yaml(path)
                matches = [e for e in static_text_sensors(doc) if e.get("name") == name]
                self.assertEqual(
                    1, len(matches), f"{relpath}: expected exactly one {name!r}"
                )
                entry = matches[0]
                self.assertEqual(entry_id, entry.get("id"))
                self.assertIn("${" + substitution + "}", str(entry.get("lambda", "")))
                self.assertEqual(
                    value, str(doc.get("substitutions", {}).get(substitution))
                )
                self.assertIn(
                    entry_id, {pid for pid, _ in boot_published_ids(doc)}, relpath
                )

    def test_no_package_declares_a_generic_identity_substitution(self) -> None:
        offenders: List[str] = []
        for path in yaml_files():
            subs = load_yaml(path).get("substitutions")
            if not isinstance(subs, dict):
                continue
            for banned in BANNED_GENERIC_IDENTITY_SUBSTITUTIONS:
                if banned in subs:
                    offenders.append(f"{rel(path)}: {banned}")
        self.assertEqual(
            [],
            offenders,
            "Generic board-identity substitutions collide in ESPHome's flat "
            "substitution namespace — use board-specific names:\n  "
            + "\n  ".join(offenders),
        )


# --- substitution isolation across combined compositions --------------------


class SubstitutionIsolationTests(unittest.TestCase):
    """AirIQ / VentIQ / RoomIQ cannot overwrite each other's identity."""

    IDENTITY_KEYS = {
        substitution for (_id, _name, substitution, _v) in BOARD_SKU_ENTITIES.values()
    }

    def test_no_composition_has_a_conflicting_identity_substitution(self) -> None:
        conflicts: List[str] = []
        for product in product_entry_points():
            declarations: Dict[str, Dict[str, str]] = {}
            for path in composed_files(product):
                subs = load_yaml(path).get("substitutions")
                if not isinstance(subs, dict):
                    continue
                for key in self.IDENTITY_KEYS:
                    if key in subs:
                        declarations.setdefault(key, {})[rel(path)] = str(subs[key])
            for key, sources in declarations.items():
                if len(set(sources.values())) > 1:
                    conflicts.append(f"{rel(product)}: {key} -> {sources}")
        self.assertEqual(
            [],
            conflicts,
            "Two packages in one composition declare the same identity "
            "substitution with different values; the later-declared package "
            "silently wins for BOTH entities:\n  " + "\n  ".join(conflicts),
        )

    def _assert_board_sku(self, product: Path, relpath: str) -> None:
        entry_id, name, substitution, value = BOARD_SKU_ENTITIES[relpath]
        subs = resolve_substitutions(product)
        self.assertIn(
            substitution,
            subs,
            f"{rel(product)} does not compose {relpath}",
        )
        self.assertEqual(
            value,
            subs[substitution],
            f"{rel(product)}: {name} resolves to {subs[substitution]!r}, "
            f"not {value!r} — another board overwrote its identity",
        )

    def test_combined_airiq_roomiq_keeps_both_module_skus(self) -> None:
        product = PRODUCTS_DIR / "bundles" / "ceiling-poe-airiq-roomiq.yaml"
        self.assertTrue(product.is_file(), product)
        self._assert_board_sku(product, "packages/boards/s360-210-airiq.yaml")
        self._assert_board_sku(product, "packages/boards/s360-200-roomiq-radar.yaml")

    def test_combined_ventiq_roomiq_keeps_both_module_skus(self) -> None:
        product = PRODUCTS_DIR / "bundles" / "ceiling-poe-ventiq-roomiq.yaml"
        self.assertTrue(product.is_file(), product)
        self._assert_board_sku(product, "packages/boards/s360-211-ventiq.yaml")
        self._assert_board_sku(product, "packages/boards/s360-200-roomiq-radar.yaml")

    def test_led_and_roomiq_composition_keeps_both_skus(self) -> None:
        product = PRODUCTS_DIR / "bundles" / "ceiling-poe-roomiq-led.yaml"
        self.assertTrue(product.is_file(), product)
        self._assert_board_sku(product, "packages/boards/s360-300-led.yaml")
        self._assert_board_sku(product, "packages/boards/s360-200-roomiq-radar.yaml")


# --- runtime module status is never clobbered -------------------------------


class RuntimeModuleStatusTests(unittest.TestCase):
    """A runtime owner always wins over the compile-time seed value."""

    def setUp(self) -> None:
        self.doc = load_yaml(DEVICE_FRAMEWORK)

    def test_seed_publication_precedes_every_runtime_framework_hook(self) -> None:
        priorities = {
            priority
            for entry_id, priority in boot_published_ids(self.doc)
            if entry_id in MODULE_STATUS_ENTITIES
        }
        self.assertTrue(priorities, "module status is never seeded at boot")
        for priority in priorities:
            self.assertGreater(
                priority,
                RUNTIME_FRAMEWORK_BOOT_PRIORITY,
                "the compile-time seed must run BEFORE the runtime "
                "frameworks' boot hooks (a higher priority runs earlier)",
            )

    def test_runtime_framework_hooks_stay_at_their_own_priority(self) -> None:
        """Nothing at or above the seed priority may touch module status.

        A runtime framework may publish its own compile-time strings at
        priority ``STATIC_PUBLISH_BOOT_PRIORITY``, but its module-status
        evaluation must stay at its own (numerically lower, therefore later)
        boot priority so the seed can never win a race with it.
        """
        for relpath in {
            owner for (_n, _s, owner) in MODULE_STATUS_ENTITIES.values() if owner
        }:
            with self.subTest(framework=relpath):
                doc = load_yaml(REPO_ROOT / relpath)
                static_ids = {e.get("id") for e in static_text_sensors(doc)}
                for hook in on_boot_entries(doc):
                    if hook.get("priority", 0) <= RUNTIME_FRAMEWORK_BOOT_PRIORITY:
                        continue
                    for action in _iter_actions(hook.get("then")):
                        if not isinstance(action, dict):
                            continue
                        updated = action.get("component.update")
                        self.assertIn(
                            updated,
                            static_ids,
                            f"{relpath}: only this package's own static "
                            f"diagnostics may publish at priority "
                            f"{STATIC_PUBLISH_BOOT_PRIORITY}; module-status "
                            f"evaluation must stay at "
                            f"{RUNTIME_FRAMEWORK_BOOT_PRIORITY} or later",
                        )

    def test_module_status_is_seeded_once_and_never_re_applied(self) -> None:
        published = [
            entry_id
            for entry_id, _ in boot_published_ids(self.doc)
            if entry_id in MODULE_STATUS_ENTITIES
        ]
        for entry_id in MODULE_STATUS_ENTITIES:
            self.assertEqual(
                1,
                published.count(entry_id),
                f"{entry_id} must be published exactly once at boot",
            )
        self.assertNotIn(
            "interval",
            self.doc,
            "the device framework must not poll compile-time identity on a "
            "timer — that would reset runtime module status",
        )
        self.assertNotIn(
            "script",
            self.doc,
            "the device framework owns no repeating publisher",
        )

    def test_presence_module_status_has_a_runtime_publisher(self) -> None:
        # SENSE360-CANONICALISATION-001 PR 10: the runtime publisher and the
        # 500 ms tick moved into the sense360_presence component glue; the
        # framework binds the Core-Framework-owned entity to it by id.
        text = (REPO_ROOT / "packages/features/presence_framework.yaml").read_text()
        self.assertIn(
            "module_status_id: s360_module_status_presence",
            text,
            "the presence framework must bind the runtime status to the "
            "sense360_presence component",
        )
        cpp = (REPO_ROOT / "components/sense360_presence/sense360_presence.cpp").read_text()
        self.assertIn("publish_state(health)", cpp)
        self.assertIn("EVALUATE_INTERVAL_MS = 500", cpp)

    def test_presence_runtime_vocabulary_can_replace_the_seed(self) -> None:
        """Available / Degraded / Unavailable / Fault stay reachable."""
        fusion = (REPO_ROOT / "components/sense360/presence_fusion.h").read_text()
        for value in ("Available", "Degraded", "Unavailable", "Fault"):
            self.assertIn(f'"{value}"', fusion, f"{value} is not reachable")


# --- customer-facing stability ---------------------------------------------


class EntityStabilityTests(unittest.TestCase):
    """Names and ids customers automate on must not move."""

    def test_framework_entity_names_and_ids_are_unchanged(self) -> None:
        doc = load_yaml(DEVICE_FRAMEWORK)
        actual = {
            e["id"]: e.get("name")
            for e in doc.get("text_sensor", [])
            if isinstance(e, dict) and e.get("id")
        }
        for entry_id, (name, _sub) in IDENTITY_ENTITIES.items():
            self.assertEqual(name, actual.get(entry_id))
        for entry_id, (name, _sub, _owner) in MODULE_STATUS_ENTITIES.items():
            self.assertEqual(name, actual.get(entry_id))

    def test_product_identification_entities_keep_their_names(self) -> None:
        """Adding ids must not touch the `${friendly_name} ...` names."""
        expected_suffixes = (
            "Product SKU",
            "Firmware Version",
            "WebFlash Config",
            "Product Config",
        )
        bad: List[str] = []
        for product in product_entry_points():
            for entry in static_text_sensors(load_yaml(product)):
                name = str(entry.get("name", ""))
                if not name.startswith("${friendly_name} "):
                    continue
                if not name.endswith(expected_suffixes):
                    bad.append(f"{rel(product)}: {name}")
        self.assertEqual([], bad, "\n  ".join(bad))

    def test_product_identification_entities_use_the_pinned_ids(self) -> None:
        for product in product_entry_points():
            doc = load_yaml(product)
            statics = static_text_sensors(doc)
            if not statics:
                continue
            with self.subTest(product=rel(product)):
                ids = [e.get("id") for e in statics]
                for entry_id in ids:
                    self.assertIn(entry_id, PRODUCT_IDENTITY_IDS)
                self.assertEqual(
                    len(ids), len(set(ids)), "duplicate ids inside one product"
                )


# --- representative composition validation (needs the ESPHome CLI) ----------

PLACEHOLDER_SECRETS = """\
wifi_ssid: "test-ssid"
wifi_password: "test-password-1234"
api_encryption_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa="
ota_password: "test-ota-password-1234"
fallback_ap_password: "test-fallback-1234"
"""

# The representative remote consumer named by STATIC-DIAGNOSTIC-PUBLISH-001:
# Core + LED + RoomIQ + Presence, declaring its identity through the
# documented top-level substitutions.
CONSUMER_CORE_LED_ROOMIQ_PRESENCE = """\
substitutions:
  # ESPHome caps hostnames at 31 characters.
  device_name: s360-core-led-roomiq-pres
  friendly_name: Sense360 Core LED RoomIQ Presence
  timezone: "Europe/London"
  device_version: "custom-remote"
  sense360_remote_url: file://__REMOTE__
  sense360_remote_ref: main
  s360_config_string: "Ceiling-Core-LED-RoomIQ-Presence"
  s360_hardware_model: "S360-100"
  s360_hardware_revision: "R4"
  s360_capabilities: "core,led,roomiq,presence"
  s360_capabilities_human: "Core, LED, RoomIQ, Presence"
  s360_module_led: "Included"
  s360_module_roomiq: "Included"
  s360_module_presence: "Included"
  led_has_roomiq: "true"
  led_has_presence: "true"

packages:
  core:
    url: file://__REMOTE__
    ref: main
    files: [packages/hardware/sense360_core_ceiling.yaml]
    refresh: 0s
  core_framework:
    url: file://__REMOTE__
    ref: main
    files: [packages/base/device_framework.yaml]
    refresh: 0s
  led_board:
    url: file://__REMOTE__
    ref: main
    files: [packages/boards/s360-300-led.yaml]
    refresh: 0s
  roomiq_presence:
    url: file://__REMOTE__
    ref: main
    files: [packages/remote/ceiling-roomiq-presence.yaml]
    refresh: 0s
  led_framework:
    url: file://__REMOTE__
    ref: main
    files: [packages/remote/led-framework.yaml]
    refresh: 0s
  led_presence_bridge:
    url: file://__REMOTE__
    ref: main
    files: [packages/features/led_presence_bridge.yaml]
    refresh: 0s

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: DEBUG
"""


def _esphome_cli() -> Optional[str]:
    return shutil.which("esphome")


def _build_local_remote(dest: Path) -> None:
    """Snapshot the working tree into a throwaway git repo (repo convention)."""
    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()
    for relpath in tracked + untracked:
        src = REPO_ROOT / relpath
        if not src.is_file():
            continue
        dst = dest / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@sense360.test",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@sense360.test",
    }
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture"], cwd=dest, check=True, env=env
    )


class _RemoteFixture:
    def __init__(self, consumer_yaml: str) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="s360-static-pub-"))
        self.consumer = self.work / "consumer"
        self.consumer.mkdir()
        (self.consumer / "secrets.yaml").write_text(PLACEHOLDER_SECRETS)
        remote = self.work / "remote"
        remote.mkdir()
        _build_local_remote(remote)
        (self.consumer / "device.yaml").write_text(
            consumer_yaml.replace("__REMOTE__", str(remote))
        )
        self.cache = self.work / "esphome-data"

    def run(self, command: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "ESPHOME_DATA_DIR": str(self.cache)}
        return subprocess.run(
            [_esphome_cli(), command, str(self.consumer / "device.yaml")],
            cwd=self.consumer,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.work, ignore_errors=True)


@unittest.skipIf(_esphome_cli() is None, "esphome CLI not installed")
class RemoteConsumerPublicationTests(unittest.TestCase):
    """Core + LED + RoomIQ + Presence resolves and publishes its identity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _RemoteFixture(CONSUMER_CORE_LED_ROOMIQ_PRESENCE)
        cls.result = cls.fixture.run("config")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.cleanup()

    def test_configuration_validates(self) -> None:
        self.assertEqual(
            0, self.result.returncode, f"esphome config failed:\n{self.result.stdout}"
        )

    def test_compiled_identity_values_are_present(self) -> None:
        out = self.result.stdout
        for value in (
            "custom-remote",
            "Ceiling-Core-LED-RoomIQ-Presence",
            "S360-100",
            "R4",
            "Core, LED, RoomIQ, Presence",
        ):
            self.assertIn(value, out, f"{value!r} missing from the resolved config")

    def test_identity_entities_are_published_at_boot(self) -> None:
        # The validated dump renders the action as a mapping:
        #     - component.update:
        #         id: s360_product_configuration
        published = set(
            re.findall(r"component\.update:\s*\n\s*id:\s*(\S+)", self.result.stdout)
        )
        for entry_id in (
            list(IDENTITY_ENTITIES)
            + list(MODULE_STATUS_ENTITIES)
            + ["s360_led_ring_sku", "s360_presence_module_sku"]
        ):
            self.assertIn(
                entry_id,
                published,
                f"{entry_id} has no boot publication in the resolved config",
            )

    def test_static_publication_runs_before_the_runtime_frameworks(self) -> None:
        """Boot priorities in the merged config keep the seed ordering."""
        priorities = [
            float(p)
            for p in re.findall(r"^\s+- priority: (\S+)$", self.result.stdout, re.M)
        ]
        self.assertIn(float(STATIC_PUBLISH_BOOT_PRIORITY), priorities)
        self.assertIn(float(RUNTIME_FRAMEWORK_BOOT_PRIORITY), priorities)

    def test_led_boot_hook_survives_package_merging(self) -> None:
        """Map-form on_boot used to delete other packages' boot hooks."""
        self.assertIn("sense360::ledfw", self.result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

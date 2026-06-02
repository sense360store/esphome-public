#!/usr/bin/env python3
"""Regression guard for the preview WebFlash wrappers.

RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001.

Locks the invariants of the three ``products/webflash`` wrapper YAMLs added for
the compile-validated webflash-lane preview candidates
(``Ceiling-POE-AirIQ-RoomIQ``, ``Ceiling-POE-RoomIQ``,
``Ceiling-POE-RoomIQ-LED``):

  * the three wrapper files exist;
  * each wrapper resolves to a valid ``products/sense360-*.yaml`` product shim
    (which in turn re-includes its ``products/bundles`` composition);
  * each wrapper is preview-only — it declares only a ``packages:`` block with
    no ``version`` / ``channel`` / ``artifact_name`` publication metadata and
    makes no stable / hardware-verification claim;
  * the preview target manifest (``config/preview-release-targets.json``)
    records each wrapper in a ``webflash_wrapper`` field, keeps the target
    ``preview`` / ``eligible-unpublished``, and keeps a non-empty build blocker;
  * the stable baseline (``Ceiling-POE-VentIQ-RoomIQ``) and the published LED
    preview (``Ceiling-POE-VentIQ-RoomIQ-LED``) target rows are unchanged;
  * NO TRIAC wrapper was added (FanTRIAC stays advanced-manual-preview, blocked
    by HW-005, with no ``webflash_wrapper``);
  * NO fan manual-preview wrapper was added (FanRelay / FanPWM / FanDAC stay on
    the manual-preview lane, off the WebFlash lane, with no wrapper on disk);
  * NO ``config/webflash-builds.json`` build row was added by this PR.

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_webflash_wrappers.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_preview_release_targets import validate  # noqa: E402

PRODUCTS_DIR = REPO_ROOT / "products"
WEBFLASH_WRAPPER_DIR = PRODUCTS_DIR / "webflash"
MANIFEST_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"

# The three wrappers this PR adds, keyed by WebFlash config string.
NEW_WRAPPERS = {
    "Ceiling-POE-AirIQ-RoomIQ": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
    "Ceiling-POE-RoomIQ": "products/webflash/ceiling-poe-roomiq.yaml",
    "Ceiling-POE-RoomIQ-LED": "products/webflash/ceiling-poe-roomiq-led.yaml",
}
EXPECTED_SHIM = {
    "Ceiling-POE-AirIQ-RoomIQ": "products/sense360-ceiling-poe-airiq-roomiq.yaml",
    "Ceiling-POE-RoomIQ": "products/sense360-ceiling-poe-roomiq.yaml",
    "Ceiling-POE-RoomIQ-LED": "products/sense360-ceiling-poe-roomiq-led.yaml",
}

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
FANTRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC")
TRIAC_TOKEN = "FanTRIAC"

# Artifact-publication metadata that must never appear in a preview wrapper.
ARTIFACT_METADATA_KEYS = ("version", "channel", "artifact_name", "substitutions")


def _esphome_tag_constructor(loader, node):
    """Accept ESPHome custom tags without resolving them (mirror validate_configs)."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
    yaml.add_constructor(_tag, _esphome_tag_constructor, Loader=yaml.SafeLoader)
yaml.add_multi_constructor(
    "!include_dir_", _esphome_tag_constructor, Loader=yaml.SafeLoader
)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _single_include(packages: Dict[str, Any]) -> str:
    """Return the lone ``!include`` target string from a wrapper packages block."""
    values = list(packages.values())
    assert len(values) == 1, f"expected exactly one package, got {values!r}"
    target = values[0]
    assert (
        isinstance(target, str) and target
    ), f"include target not a string: {target!r}"
    return target


def _wrapper_files() -> List[str]:
    if not WEBFLASH_WRAPPER_DIR.is_dir():
        return []
    return sorted(p.name for p in WEBFLASH_WRAPPER_DIR.glob("*.yaml"))


class WrapperFilesExistTests(unittest.TestCase):
    """Task item: wrapper files exist; wrappers resolve to valid product shims."""

    def test_three_wrapper_files_exist(self) -> None:
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                self.assertTrue(
                    (REPO_ROOT / rel).is_file(),
                    f"missing wrapper for {cs}: {rel}",
                )

    def test_wrapper_basename_follows_naming_convention(self) -> None:
        # Existing convention: wrapper basename is the lowercased config string.
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                self.assertEqual(Path(rel).name, f"{cs.lower()}.yaml")

    def test_wrappers_resolve_to_valid_product_shims(self) -> None:
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                wrapper = REPO_ROOT / rel
                cfg = _load_yaml(wrapper)
                self.assertIsInstance(cfg, dict)
                self.assertIn("packages", cfg)
                include = _single_include(cfg["packages"])
                # The include must point at the matching sense360-* shim.
                resolved = (wrapper.parent / include).resolve()
                self.assertEqual(
                    resolved,
                    (REPO_ROOT / EXPECTED_SHIM[cs]).resolve(),
                    f"{cs}: wrapper includes {include!r}, expected the shim "
                    f"{EXPECTED_SHIM[cs]}",
                )
                self.assertTrue(resolved.is_file(), f"shim missing: {resolved}")

    def test_shims_resolve_to_bundle_composition(self) -> None:
        # wrapper -> products/sense360-*.yaml shim -> products/bundles/*.yaml.
        for cs in NEW_WRAPPERS:
            with self.subTest(config_string=cs):
                shim = REPO_ROOT / EXPECTED_SHIM[cs]
                cfg = _load_yaml(shim)
                self.assertIn("packages", cfg)
                include = _single_include(cfg["packages"])
                resolved = (shim.parent / include).resolve()
                self.assertTrue(
                    resolved.is_file(),
                    f"{cs}: shim include {include!r} does not resolve to a file",
                )
                self.assertIn("products/bundles/", resolved.as_posix())


class WrapperContentTests(unittest.TestCase):
    """Task item: preview-only, no artifact metadata, no stable/hardware claim."""

    def test_wrappers_carry_only_a_packages_block(self) -> None:
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                cfg = _load_yaml(REPO_ROOT / rel)
                self.assertEqual(
                    sorted(cfg.keys()),
                    ["packages"],
                    f"{cs}: wrapper must declare ONLY a packages block, got "
                    f"{sorted(cfg.keys())}",
                )

    def test_wrappers_declare_no_artifact_publication_metadata(self) -> None:
        for cs, rel in NEW_WRAPPERS.items():
            cfg = _load_yaml(REPO_ROOT / rel)
            for key in ARTIFACT_METADATA_KEYS:
                with self.subTest(config_string=cs, key=key):
                    self.assertNotIn(
                        key,
                        cfg,
                        f"{cs}: preview wrapper must not declare {key!r}",
                    )

    def test_wrappers_do_not_name_a_stable_artifact(self) -> None:
        # A preview wrapper must not embed a stable artifact name / channel.
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                self.assertNotIn(
                    "-stable.bin",
                    text,
                    f"{cs}: preview wrapper must not reference a stable artifact",
                )

    def test_wrappers_disclaim_stable_and_preview_status(self) -> None:
        # The header must positively mark the wrapper preview and NOT stable.
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                lower = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("preview", lower)
                self.assertIn("not stable", lower)


class ManifestReferencesWrappersTests(unittest.TestCase):
    """Task item: preview target manifest references valid wrappers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)
        cls.by_cs = {t["config_string"]: t for t in cls.manifest["targets"]}

    def test_each_wrapped_target_records_its_wrapper(self) -> None:
        for cs, rel in NEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                target = self.by_cs.get(cs)
                self.assertIsNotNone(target, f"no manifest target for {cs}")
                self.assertEqual(target.get("webflash_wrapper"), rel)
                self.assertTrue(
                    (REPO_ROOT / target["webflash_wrapper"]).is_file(),
                    f"{cs}: webflash_wrapper path does not exist",
                )

    def test_wrapped_targets_stay_preview_and_unpublished(self) -> None:
        for cs in NEW_WRAPPERS:
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertEqual(t["channel_tier"], "preview")
                self.assertTrue(t["is_preview_target"])
                self.assertEqual(t["delivery_lane"], "webflash")
                self.assertEqual(t["publication_status"], "eligible-unpublished")
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])
                # Import/publish stays gated: a non-empty build blocker remains.
                self.assertTrue(
                    t["build_blocker"],
                    f"{cs}: must keep a non-empty build_blocker (gated on the "
                    "later build-row PR)",
                )

    def test_manifest_still_validates_clean(self) -> None:
        errors = validate(
            self.manifest,
            _load_json(POLICY_PATH),
            _load_json(COMPAT_PATH),
            _load_json(BUILDS_PATH),
            _load_json(CATALOG_PATH),
            _load_json(MANUAL_PATH),
        )
        self.assertEqual(errors, [], "\n".join(errors))


class StableAndLedPreviewUnchangedTests(unittest.TestCase):
    """Task items: stable target unchanged; LED preview target unchanged."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)
        cls.by_cs = {t["config_string"]: t for t in cls.manifest["targets"]}
        cls.builds = {b["config_string"] for b in _load_json(BUILDS_PATH)["builds"]}

    def test_stable_baseline_unchanged(self) -> None:
        t = self.by_cs[STABLE_CONFIG]
        self.assertEqual(t["channel_tier"], "stable")
        self.assertFalse(t["is_preview_target"])
        self.assertEqual(t["publication_status"], "published-stable")
        self.assertTrue(t["required_config"])
        self.assertIn(STABLE_CONFIG, self.builds)
        # This PR adds no wrapper reference to the stable baseline row.
        self.assertNotIn("webflash_wrapper", t)

    def test_led_preview_unchanged(self) -> None:
        t = self.by_cs[LED_PREVIEW_CONFIG]
        self.assertEqual(t["channel_tier"], "preview")
        self.assertEqual(t["publication_status"], "published-preview")
        self.assertIn(LED_PREVIEW_CONFIG, self.builds)
        # The published VentIQ LED preview row is not touched by this PR.
        self.assertNotIn("webflash_wrapper", t)

    def test_new_roomiq_led_is_distinct_from_published_ventiq_led(self) -> None:
        # The new RoomIQ+LED preview must not collide with the published
        # VentIQ+RoomIQ+LED preview.
        self.assertIn("Ceiling-POE-RoomIQ-LED", self.by_cs)
        self.assertNotEqual("Ceiling-POE-RoomIQ-LED", LED_PREVIEW_CONFIG)
        self.assertNotIn("Ceiling-POE-RoomIQ-LED", self.builds)


class NoTriacWrapperTests(unittest.TestCase):
    """Hard guardrail: no TRIAC wrapper added."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)
        cls.builds = {b["config_string"] for b in _load_json(BUILDS_PATH)["builds"]}

    def test_no_new_wrapper_carries_a_triac_token(self) -> None:
        for cs in NEW_WRAPPERS:
            self.assertNotIn(TRIAC_TOKEN, cs.split("-"))

    def test_no_triac_wrapper_file_added(self) -> None:
        # The only fantriac wrapper on disk is the pre-existing BLOCKED/REFERENCE
        # file; this PR adds no new TRIAC wrapper.
        triac_wrappers = [n for n in _wrapper_files() if "fantriac" in n.lower()]
        self.assertEqual(
            triac_wrappers,
            ["ceiling-poe-ventiq-fantriac-roomiq.yaml"],
            "no NEW TRIAC wrapper may be added; only the pre-existing reference "
            f"wrapper may exist, found {triac_wrappers!r}",
        )

    def test_triac_target_has_no_wrapper_and_stays_gated(self) -> None:
        triac = [t for t in self.manifest["targets"] if t.get("is_triac")]
        self.assertEqual(len(triac), 1)
        t = triac[0]
        self.assertEqual(t["config_string"], FANTRIAC_CONFIG)
        self.assertNotIn("webflash_wrapper", t)
        self.assertEqual(t["delivery_lane"], "advanced-manual-preview")
        self.assertFalse(t["webflash_import_eligibility"]["eligible"])
        self.assertNotIn(FANTRIAC_CONFIG, self.builds)


class NoFanWrapperTests(unittest.TestCase):
    """Hard guardrail: no fan manual-preview wrapper added (policy unchanged)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)

    def test_no_fan_wrapper_file_on_disk(self) -> None:
        offenders = [
            n
            for n in _wrapper_files()
            if any(tok.lower() in n.lower() for tok in FAN_DRIVER_TOKENS)
        ]
        self.assertEqual(
            offenders,
            [],
            f"no fan manual-preview wrapper may be added; found {offenders!r}",
        )

    def test_fan_targets_have_no_wrapper_and_stay_manual_preview(self) -> None:
        fans = [
            t
            for t in self.manifest["targets"]
            if t.get("is_fan") and not t.get("is_triac")
        ]
        self.assertEqual({t["family"] for t in fans}, {"FanRelay", "FanPWM", "FanDAC"})
        for t in fans:
            with self.subTest(config_string=t["config_string"]):
                self.assertNotIn("webflash_wrapper", t)
                self.assertEqual(t["delivery_lane"], "manual-preview")
                self.assertFalse(t["webflash_import_eligibility"]["eligible"])


class NoWebflashBuildRowsAddedTests(unittest.TestCase):
    """Hard guardrail: no config/webflash-builds.json row added by this PR."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.builds_doc = _load_json(BUILDS_PATH)
        cls.builds = cls.builds_doc["builds"]
        cls.by_cs = {b["config_string"] for b in cls.builds}

    def test_build_ledger_is_exactly_the_two_live_builds(self) -> None:
        # This PR is wrappers-only: the ledger stays the pre-existing stable +
        # LED preview rows. A build row for a wrapped preview is a later PR.
        self.assertEqual(self.by_cs, {STABLE_CONFIG, LED_PREVIEW_CONFIG})

    def test_new_wrapped_config_strings_absent_from_ledger(self) -> None:
        for cs in NEW_WRAPPERS:
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, self.by_cs)

    def test_new_wrappers_not_referenced_as_a_build_product_yaml(self) -> None:
        product_yamls = {b.get("product_yaml") for b in self.builds}
        for rel in NEW_WRAPPERS.values():
            with self.subTest(wrapper=rel):
                self.assertNotIn(rel, product_yamls)


if __name__ == "__main__":
    unittest.main(verbosity=2)

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
  * each wrapper is a thin re-export — it declares only a ``packages:`` block
    with no ``version`` / ``channel`` / ``artifact_name`` publication metadata;
  * the preview target manifest (``config/preview-release-targets.json``)
    records each wrapper in a ``webflash_wrapper`` field;
  * the stable baseline (``Ceiling-POE-VentIQ-RoomIQ``) and the published LED
    preview (``Ceiling-POE-VentIQ-RoomIQ-LED``) target rows are unchanged.

RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 cut the reviewed
``config/webflash-builds.json`` PREVIEW build rows for the three wrapped
candidates; STABLE-PROMOTION-RECONCILE-001 then promoted Bedroom
(``Ceiling-POE-RoomIQ``, v1.0.5, 2026-06-08) and Kitchen
(``Ceiling-POE-AirIQ-RoomIQ``, v1.0.6, 2026-06-09) to the stable channel under
owner risk-acceptance waivers. CI-PIPELINE-CLARITY-001 P4a then de-listed the
never-built ``Ceiling-POE-RoomIQ-LED`` row.

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record, 2026-07-09)
retired the bench-proof documentation requirement as a release gate; hardware
readiness is now owner-declared. Under that declaration the build ledger grew
nine release-eligibility-metadata rows (release_state
``metadata-ready-unpublished``; no binary / Release / tag / manifest cut):

  * ``Ceiling-POE-RoomIQ-LED`` was RE-LISTED on the preview channel,
    deliberately reversing the CI-PIPELINE-CLARITY-001 P4a de-list;
  * six FanPWM / FanDAC configs landed on the preview channel and two FanRelay
    room bundles landed on the experimental channel only, each addressed via a
    NEW thin ``products/webflash`` fan wrapper.

The former "no fan row in config/webflash-builds.json" guardrail was therefore
revised by the owner into CHANNEL teeth, guarded below: fan configs are NEVER
on the stable channel (FanRelay/FanTRIAC → experimental; FanPWM/FanDAC →
preview), never in release_one_required_configs, and their commercial posture
keeps buyable / recommended / customer_default / stable false.

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

HW_RELEASE_DECISION = "HW-RELEASE-001"
HW_RELEASE_DOC = "docs/hw-release-001.md"

# The three wrapper files RELEASE-PREVIEW-WEBFLASH-WRAPPERS-001 added, keyed by
# WebFlash config string.
NEW_WRAPPERS = {
    "Ceiling-POE-AirIQ-RoomIQ": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
    "Ceiling-POE-RoomIQ": "products/webflash/ceiling-poe-roomiq.yaml",
    "Ceiling-POE-RoomIQ-LED": "products/webflash/ceiling-poe-roomiq-led.yaml",
}
# STABLE-PROMOTION-RECONCILE-001: two of the three wrapped bundles were promoted
# to the stable channel (Bedroom v1.0.5 on 2026-06-08, Kitchen v1.0.6 on
# 2026-06-09, both owner-waiver promotions; binaries are published). Their
# wrappers are now STABLE wrappers.
PROMOTED_WRAPPERS = {
    "Ceiling-POE-RoomIQ": "products/webflash/ceiling-poe-roomiq.yaml",
}
# HW-RELEASE-001 RE-LISTED Ceiling-POE-RoomIQ-LED on the preview channel
# (release-eligibility metadata only), deliberately reversing the
# CI-PIPELINE-CLARITY-001 P4a de-list. Its preserved wrapper is live again.
PREVIEW_WRAPPERS = {
    "Ceiling-POE-AirIQ-RoomIQ": "products/webflash/ceiling-poe-airiq-roomiq.yaml",
    "Ceiling-POE-RoomIQ-LED": "products/webflash/ceiling-poe-roomiq-led.yaml",
}
# Wrappers whose config_string resolves in the live config/webflash-builds
# ledger (the promoted stable rows plus the re-listed preview row).
LEDGER_WRAPPERS = {**PROMOTED_WRAPPERS, **PREVIEW_WRAPPERS}
EXPECTED_SHIM = {
    "Ceiling-POE-AirIQ-RoomIQ": "products/sense360-ceiling-poe-airiq-roomiq.yaml",
    "Ceiling-POE-RoomIQ": "products/sense360-ceiling-poe-roomiq.yaml",
    "Ceiling-POE-RoomIQ-LED": "products/sense360-ceiling-poe-roomiq-led.yaml",
}

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
RELISTED_LED_CONFIG = "Ceiling-POE-RoomIQ-LED"
FANTRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC")
TRIAC_TOKEN = "FanTRIAC"

# HW-RELEASE-001: the eight NEW fan wrappers, keyed by config string, mapped to
# the ONLY channel each may occupy (FanPWM / FanDAC → preview; the FanRelay
# room bundles → experimental only, mirroring the COMPLIANCE-001 lane posture).
FAN_WRAPPER_CHANNELS = {
    "Ceiling-POE-FanPWM": "preview",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ": "preview",
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ": "preview",
    "Ceiling-POE-FanDAC": "preview",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ": "preview",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ": "preview",
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ": "experimental",
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ": "experimental",
}
FAN_WRAPPERS = {
    cs: f"products/webflash/{cs.lower()}.yaml" for cs in FAN_WRAPPER_CHANNELS
}
# All HW-RELEASE-001 metadata rows (the re-listed LED preview + the eight fan
# rows) and the only channel each may occupy.
HW_RELEASE_ROW_CHANNELS = {RELISTED_LED_CONFIG: "preview", **FAN_WRAPPER_CHANNELS}

# Artifact-publication metadata that must never appear in a wrapper.
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
    """Task item: thin re-exports, no artifact metadata, no stable claim."""

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

    def test_preview_wrappers_do_not_name_a_stable_artifact(self) -> None:
        # A preview wrapper must not embed a stable artifact name / channel.
        for cs, rel in PREVIEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                self.assertNotIn(
                    "-stable.bin",
                    text,
                    f"{cs}: preview wrapper must not reference a stable artifact",
                )

    def test_preview_wrappers_disclaim_stable_and_preview_status(self) -> None:
        # The header must positively mark the wrapper preview and NOT stable.
        for cs, rel in PREVIEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                lower = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("preview", lower)
                self.assertIn("not stable", lower)

    def test_promoted_wrappers_identify_as_stable_under_waiver(self) -> None:
        # STABLE-PROMOTION-RECONCILE-001: the promoted wrappers must say they
        # are stable, cite the owner waiver basis, and no longer carry the
        # preview-candidate "not stable" disclaimer (the binary IS stable now).
        for cs, rel in PROMOTED_WRAPPERS.items():
            with self.subTest(config_string=cs):
                lower = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("stable", lower)
                self.assertIn("waiver", lower)
                self.assertNotIn(
                    "not stable",
                    lower,
                    f"{cs}: promoted wrapper must not still claim it is not stable",
                )
                # Never recommended / a customer default by the promotion alone.
                self.assertIn("not recommended", lower)


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

    def test_relisted_led_target_is_preview_and_back_in_the_ledger(self) -> None:
        # HW-RELEASE-001 RE-LISTED Ceiling-POE-RoomIQ-LED (inverting the
        # CI-PIPELINE-CLARITY-001 P4a de-list guard this test used to be): the
        # ledger row exists again, on the preview channel, addressed via the
        # preserved wrapper, and the reconciled manifest target is back to
        # metadata-ready with its build_blocker resolved. No published binary
        # is claimed (release_state stays metadata-ready-unpublished; no .bin /
        # Release / tag was cut).
        builds = {b["config_string"]: b for b in _load_json(BUILDS_PATH)["builds"]}
        for cs, rel in PREVIEW_WRAPPERS.items():
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertEqual(t["channel_tier"], "preview")
                self.assertEqual(t["delivery_lane"], "webflash")
                self.assertEqual(t.get("webflash_wrapper"), rel)
                self.assertTrue((REPO_ROOT / rel).is_file())
                self.assertEqual(
                    t["publication_status"], "webflash-preview-metadata-ready"
                )
                self.assertIsNone(t["build_blocker"])
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])
                # Stable stays gated; no published binary is claimed.
                self.assertTrue(t["stable_blocker"])
                self.assertFalse(
                    str(t["publication_status"]).startswith("published"),
                    f"{cs}: no publication may be claimed for a metadata row",
                )
                # The ledger row is live again (HW-RELEASE-001).
                self.assertIn(cs, builds)
                row = builds[cs]
                self.assertEqual(row["channel"], "preview")
                self.assertEqual(row["product_yaml"], rel)
                self.assertEqual(row["release_state"], "metadata-ready-unpublished")
                if cs == "Ceiling-POE-RoomIQ-LED":
                    self.assertEqual(row["owner_declaration"], HW_RELEASE_DOC)

    def test_promoted_wrapped_targets_are_published_stable(self) -> None:
        # STABLE-PROMOTION-RECONCILE-001: Bedroom (v1.0.5) and Kitchen (v1.0.6)
        # were promoted and their stable binaries are published. Their targets
        # are stable-tier / published-stable but still NOT recommended / NOT a
        # customer default / NOT required-config (the promotions ride owner
        # waivers; only Release-One is the customer baseline).
        for cs in PROMOTED_WRAPPERS:
            with self.subTest(config_string=cs):
                t = self.by_cs[cs]
                self.assertEqual(t["channel_tier"], "stable")
                self.assertFalse(t["is_preview_target"])
                self.assertEqual(t["delivery_lane"], "webflash")
                self.assertEqual(t["publication_status"], "published-stable")
                self.assertIsNone(t["build_blocker"])
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])
                self.assertFalse(t["customer_kit_default"])
                self.assertTrue(t["expected_artifact_name"].endswith("-stable.bin"))

    def test_manifest_still_validates_clean(self) -> None:
        # The manifest / validator were reconciled to the HW-RELEASE-001
        # posture, so validation is clean again against the 14-row ledger.
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
        cls.builds = {b["config_string"]: b for b in _load_json(BUILDS_PATH)["builds"]}

    def test_stable_baseline_unchanged(self) -> None:
        t = self.by_cs[STABLE_CONFIG]
        self.assertEqual(t["channel_tier"], "stable")
        self.assertFalse(t["is_preview_target"])
        self.assertEqual(t["publication_status"], "published-stable")
        self.assertTrue(t["required_config"])
        self.assertIn(STABLE_CONFIG, self.builds)
        # No wrapper reference was ever added to the stable baseline row.
        self.assertNotIn("webflash_wrapper", t)

    def test_led_preview_unchanged(self) -> None:
        t = self.by_cs[LED_PREVIEW_CONFIG]
        self.assertEqual(t["channel_tier"], "preview")
        self.assertEqual(t["publication_status"], "published-preview")
        self.assertIn(LED_PREVIEW_CONFIG, self.builds)
        # The published VentIQ LED preview row is not touched.
        self.assertNotIn("webflash_wrapper", t)

    def test_relisted_roomiq_led_is_distinct_from_published_ventiq_led(self) -> None:
        # Ceiling-POE-RoomIQ-LED is a distinct config string from the published
        # VentIQ+RoomIQ+LED preview. HW-RELEASE-001 RE-LISTED it on the preview
        # channel (v1.0.0, metadata-ready-unpublished), reversing the
        # CI-PIPELINE-CLARITY-001 P4a de-list, while the published VentIQ LED
        # preview stays exactly the unchanged v1.0.1 preview row.
        self.assertNotEqual(RELISTED_LED_CONFIG, LED_PREVIEW_CONFIG)
        self.assertIn(RELISTED_LED_CONFIG, self.builds)
        relisted = self.builds[RELISTED_LED_CONFIG]
        self.assertEqual(relisted["channel"], "preview")
        self.assertEqual(relisted["version"], "1.0.0")
        self.assertEqual(relisted["release_state"], "metadata-ready-unpublished")
        self.assertIn(LED_PREVIEW_CONFIG, self.builds)
        ventiq_led = self.builds[LED_PREVIEW_CONFIG]
        self.assertEqual(ventiq_led["channel"], "preview")
        self.assertEqual(ventiq_led["version"], "1.0.1")
        self.assertNotEqual(relisted["artifact_name"], ventiq_led["artifact_name"])


class NoTriacWrapperTests(unittest.TestCase):
    """Hard guardrail: no NEW TRIAC wrapper added."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)
        cls.builds = {b["config_string"] for b in _load_json(BUILDS_PATH)["builds"]}

    def test_no_new_wrapper_carries_a_triac_token(self) -> None:
        for cs in list(NEW_WRAPPERS) + list(FAN_WRAPPERS):
            self.assertNotIn(TRIAC_TOKEN, cs.split("-"))

    def test_no_triac_wrapper_file_added(self) -> None:
        # The only fantriac wrapper on disk is the pre-existing experimental
        # self-build wrapper; HW-RELEASE-001 added no new TRIAC wrapper.
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
        # The advanced-manual-preview eligibility target stays gated (no wrapper,
        # never WebFlash-import eligible). The committed config/webflash-builds.json
        # row is the SEPARATE FanTRIAC experimental self-build commissioning
        # (TRIAC-COMMISSIONING-001), admitted on the experimental channel only.
        self.assertIn(FANTRIAC_CONFIG, self.builds)
        builds_by_cs = {
            b["config_string"]: b for b in _load_json(BUILDS_PATH)["builds"]
        }
        self.assertEqual(builds_by_cs[FANTRIAC_CONFIG]["channel"], "experimental")


class FanWrapperTests(unittest.TestCase):
    """HW-RELEASE-001 inverted the old NoFanWrapperTests guard: the eight fan
    wrappers now EXIST and must be thin packages-only re-exports that never
    claim a stable channel."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = _load_json(MANIFEST_PATH)

    def test_exactly_the_eight_fan_wrapper_files_on_disk(self) -> None:
        # Inverts the pre-HW-RELEASE-001 "no fan wrapper on disk" guard: the
        # eight owner-declared fan wrappers exist, and ONLY those eight (any
        # extra fan wrapper is unreviewed drift).
        fan_files = sorted(
            n
            for n in _wrapper_files()
            if any(tok.lower() in n.lower() for tok in FAN_DRIVER_TOKENS)
        )
        self.assertEqual(
            fan_files,
            sorted(Path(rel).name for rel in FAN_WRAPPERS.values()),
            "the fan wrappers on disk must be exactly the eight HW-RELEASE-001 "
            f"wrappers; found {fan_files!r}",
        )

    def test_fan_wrappers_are_thin_packages_only_reexports(self) -> None:
        # Each fan wrapper is a thin re-export: a single !include of the
        # canonical ../sense360-<cs>.yaml shim, no artifact metadata keys.
        for cs, rel in FAN_WRAPPERS.items():
            with self.subTest(config_string=cs):
                wrapper = REPO_ROOT / rel
                self.assertTrue(wrapper.is_file(), f"missing fan wrapper {rel}")
                cfg = _load_yaml(wrapper)
                self.assertEqual(
                    sorted(cfg.keys()),
                    ["packages"],
                    f"{cs}: fan wrapper must declare ONLY a packages block",
                )
                include = _single_include(cfg["packages"])
                resolved = (wrapper.parent / include).resolve()
                expected_shim = REPO_ROOT / f"products/sense360-{cs.lower()}.yaml"
                self.assertEqual(resolved, expected_shim.resolve())
                self.assertTrue(resolved.is_file(), f"shim missing: {resolved}")
                for key in ARTIFACT_METADATA_KEYS:
                    self.assertNotIn(
                        key, cfg, f"{cs}: fan wrapper must not declare {key!r}"
                    )

    def test_fan_wrapper_headers_cite_owner_declaration_never_stable(self) -> None:
        # Every fan wrapper must cite HW-RELEASE-001 and disclaim the stable
        # channel; none may reference a stable artifact.
        for cs, rel in FAN_WRAPPERS.items():
            with self.subTest(config_string=cs):
                lower = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("hw-release-001", lower)
                self.assertTrue(
                    "never stable" in lower or "not stable" in lower,
                    f"{cs}: fan wrapper must disclaim the stable channel",
                )
                self.assertNotIn("-stable.bin", lower)

    def test_fan_targets_stay_manual_preview_and_never_stable(self) -> None:
        # The reconciled manifest enumerates the fan targets (standalone
        # drivers + HW-RELEASE-001 room bundles) on the manual-preview lane;
        # the wrapper reference lives in the ledger row (product_yaml), not in
        # the manifest fan rows. The import-eligibility tooth
        # (RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001 / ROOM-BUNDLE-FAN-
        # WEBFLASH-ELIGIBILITY-001) and the never-stable tier stand.
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
                self.assertTrue(t["webflash_import_eligibility"]["eligible"])
                self.assertNotEqual(t["channel_tier"], "stable")
                self.assertFalse(t["recommended"])
                self.assertFalse(t["customer_default"])
                self.assertFalse(t["required_config"])


class WebflashBuildRowsPresentTests(unittest.TestCase):
    """The build ledger rows are present, evidence- or declaration-bearing,
    on their governed channels, and never stable for fan configs."""

    COMPILE_RUN_ID = 26821900127

    @classmethod
    def setUpClass(cls) -> None:
        cls.builds_doc = _load_json(BUILDS_PATH)
        cls.builds = cls.builds_doc["builds"]
        cls.by_cs = {b["config_string"]: b for b in cls.builds}
        cls.required = set(
            _load_json(COMPAT_PATH).get("release_one_required_configs", [])
        )

    def test_build_ledger_is_the_fourteen_declared_builds(self) -> None:
        # Stable RoomIQ + published VentIQ LED preview + the two promoted
        # room-bundle rows + the FanTRIAC experimental self-build row
        # (TRIAC-COMMISSIONING-001) + the nine HW-RELEASE-001 metadata rows
        # (the re-listed Ceiling-POE-RoomIQ-LED preview + eight fan rows).
        self.assertEqual(
            set(self.by_cs),
            {
                STABLE_CONFIG,
                LED_PREVIEW_CONFIG,
                *LEDGER_WRAPPERS,
                FANTRIAC_CONFIG,
                *FAN_WRAPPERS,
            },
        )
        self.assertEqual(self.by_cs[FANTRIAC_CONFIG]["channel"], "experimental")

    def test_ledger_config_strings_present_in_ledger(self) -> None:
        for cs in list(LEDGER_WRAPPERS) + list(FAN_WRAPPERS):
            with self.subTest(config_string=cs):
                self.assertIn(cs, self.by_cs)

    def test_ledger_rows_point_to_their_products_webflash_wrapper(self) -> None:
        # Task item: live ledger rows point to the existing wrappers.
        for cs, rel in {**LEDGER_WRAPPERS, **FAN_WRAPPERS}.items():
            with self.subTest(config_string=cs):
                self.assertEqual(self.by_cs[cs]["product_yaml"], rel)
                self.assertTrue((REPO_ROOT / rel).is_file())

    def test_row_channels_match_their_promotion_state(self) -> None:
        # STABLE-PROMOTION-RECONCILE-001: the two promoted rows are stable with
        # stable artifact names. HW-RELEASE-001: the re-listed LED row is
        # preview with a preview artifact name.
        for cs in PREVIEW_WRAPPERS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row["channel"], "preview")
                self.assertTrue(row["artifact_name"].endswith("-preview.bin"))
                self.assertNotIn("-stable.bin", row["artifact_name"])
        for cs in PROMOTED_WRAPPERS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row["channel"], "stable")
                self.assertTrue(row["artifact_name"].endswith("-stable.bin"))

    def test_new_rows_are_not_release_one_required(self) -> None:
        # Task item: neither the wrapped candidates nor any HW-RELEASE-001 row
        # may enter release_one_required_configs.
        for cs in set(NEW_WRAPPERS) | set(HW_RELEASE_ROW_CHANNELS):
            with self.subTest(config_string=cs):
                self.assertNotIn(cs, self.required)

    def test_promoted_rows_cite_hosted_compile_evidence(self) -> None:
        # The promoted stable rows keep their compile evidence citation
        # (run 26821900127).
        for cs in PROMOTED_WRAPPERS:
            with self.subTest(config_string=cs):
                evidence = self.by_cs[cs].get("compile_evidence")
                self.assertIsInstance(evidence, dict)
                self.assertEqual(evidence.get("run_id"), self.COMPILE_RUN_ID)
                self.assertEqual(evidence.get("proof_class"), "firmware-build-only")

    def test_hw_release_rows_are_owner_declared_metadata_only(self) -> None:
        # HW-RELEASE-001 rows are release-eligibility metadata: unpublished,
        # owner-declared, on their governed channel, and no-false-proof (the
        # declaration is risk acceptance, not hardware / bench / compliance
        # proof — the notes must say so).
        for cs, channel in HW_RELEASE_ROW_CHANNELS.items():
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row["channel"], channel)
                self.assertEqual(row["release_state"], "metadata-ready-unpublished")
                if cs == "Ceiling-POE-RoomIQ-LED":
                    self.assertEqual(row["owner_declaration"], HW_RELEASE_DOC)
                self.assertEqual(
                    row["artifact_name"],
                    f"Sense360-{cs}-v1.0.0-{channel}.bin",
                )
                self.assertTrue(row["stable_blocker"])
                self.assertIn(HW_RELEASE_DECISION, row.get("notes", ""))

    def test_preview_rows_carry_release_note_warning(self) -> None:
        # Preview rows carry the preview warning key; the promoted stable rows
        # had their preview-only warning fields stripped by the promotions
        # (matching the stable Release-One row shape).
        for cs in PREVIEW_WRAPPERS:
            with self.subTest(config_string=cs):
                self.assertEqual(self.by_cs[cs].get("warning_copy_key"), "preview")
        for cs in PROMOTED_WRAPPERS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertNotIn("warning_copy_key", row)
                self.assertNotIn("release_note_warning", row)
                self.assertNotIn("release_state", row)

    def test_fan_rows_carry_lane_matched_warning_copy(self) -> None:
        # FanPWM / FanDAC preview rows use the preview warning key; the
        # FanRelay experimental rows use the experimental key AND an explicit
        # mains-adjacent release-note warning (COMPLIANCE-001 lane posture).
        for cs, channel in FAN_WRAPPER_CHANNELS.items():
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                if channel == "preview":
                    self.assertEqual(row.get("warning_copy_key"), "preview")
                else:
                    self.assertEqual(row.get("warning_copy_key"), "experimental")
                    self.assertIn("EXPERIMENTAL", row.get("release_note_warning", ""))

    def test_row_commercial_posture_is_hidden_not_buyable(self) -> None:
        # Candidate / hidden / not buyable; not recommended / default.
        # posture.stable mirrors the channel: false everywhere except the two
        # promoted stable rows.
        for cs in {**LEDGER_WRAPPERS, **FAN_WRAPPERS}:
            with self.subTest(config_string=cs):
                posture = self.by_cs[cs].get("commercial_posture", {})
                self.assertEqual(posture.get("visibility"), "hidden")
                self.assertFalse(posture.get("buyable"))
                self.assertFalse(posture.get("recommended"))
                self.assertFalse(posture.get("customer_default"))
                self.assertEqual(posture.get("stable"), cs in PROMOTED_WRAPPERS)

    def test_fan_rows_channel_teeth_never_stable(self) -> None:
        # HW-RELEASE-001 revised the former "no fan row" guardrail into CHANNEL
        # teeth, guarded here: any ledger row carrying a fan-driver token is
        # experimental (FanRelay, FanTRIAC) or preview (FanPWM, FanDAC), NEVER
        # stable, never Release-One-required, and its commercial posture keeps
        # buyable / recommended / customer_default / stable false.
        for cs, build in self.by_cs.items():
            tokens = cs.split("-")
            is_fan = any(tok in tokens for tok in FAN_DRIVER_TOKENS) or (
                TRIAC_TOKEN in tokens
            )
            if not is_fan:
                continue
            with self.subTest(config_string=cs):
                self.assertNotEqual(
                    build["channel"],
                    "stable",
                    f"{cs}: fan configs are NEVER on the stable channel",
                )
                if "FanRelay" in tokens or TRIAC_TOKEN in tokens:
                    self.assertEqual(
                        build["channel"],
                        "experimental",
                        f"{cs}: FanRelay / FanTRIAC rows are experimental-only",
                    )
                else:
                    self.assertEqual(
                        build["channel"],
                        "preview",
                        f"{cs}: FanPWM / FanDAC rows are preview-only",
                    )
                self.assertNotIn(cs, self.required)
                self.assertNotIn("-stable.bin", build["artifact_name"])
                posture = build.get("commercial_posture", {})
                self.assertFalse(posture.get("buyable"))
                self.assertFalse(posture.get("recommended"))
                self.assertFalse(posture.get("customer_default"))
                self.assertFalse(posture.get("stable"))

    def test_no_firmware_publish_side_effects_committed(self) -> None:
        # Hard guardrail: no firmware publish files changed (metadata only).
        # manifest.json / firmware/sources.json must not exist and no .bin may
        # be committed under config/ or products/.
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())
        bins = list((REPO_ROOT / "config").rglob("*.bin")) + list(
            (REPO_ROOT / "products").rglob("*.bin")
        )
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

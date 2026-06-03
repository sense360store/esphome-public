#!/usr/bin/env python3
"""STABLE-RELEASE-MATRIX-ALL-YAML-001 contract tests.

Locks in the all-YAML release matrix defined by
``docs/all-yaml-release-matrix.md`` and the classifier
``scripts/classify_all_yaml_release_matrix.py`` so the broader release
posture cannot silently regress into the prior "only RoomIQ is
release-aware" state.

The invariants enforced here:

  * **Every** YAML under ``products/`` (top-level, ``products/webflash/``,
    ``products/compile-only/``) is classified into exactly one of the six
    release classes (``stable-release``, ``preview-release``,
    ``manual-candidate-only``, ``compile-only``, ``blocked``,
    ``not-a-product-entrypoint``).
  * The release-selectable set (``stable-release`` ∪ ``preview-release``)
    equals the entries in ``config/webflash-builds.json`` — release
    selection is derived from the source of truth, not hardcoded.
  * Exactly one stable target today (``Ceiling-POE-VentIQ-RoomIQ``).
  * The preview targets today are the published VentIQ LED preview plus the
    three room-bundle preview build rows added by
    RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 (``Ceiling-POE-AirIQ-RoomIQ``,
    ``Ceiling-POE-RoomIQ``, ``Ceiling-POE-RoomIQ-LED``); LED stays preview-only
    and is **not** selectable as stable.
  * FanRelay / FanPWM / FanDAC are ``manual-candidate-only`` and are
    **not** release-selectable (and never carry an ``artifact_name``).
  * FanTRIAC is ``blocked``.
  * Every ``products/compile-only/*.yaml`` is classified ``compile-only``
    and is **not** release-selectable.
  * Helper / package YAMLs (``products/secrets.yaml``) and every WebFlash
    wrapper under ``products/webflash/`` are
    ``not-a-product-entrypoint`` and are **not** release-selectable.
  * The fan exclusion guardrail in
    ``scripts/plan_room_release_notes.py`` and
    ``scripts/list_release_targets.py`` is mirrored by the classifier:
    no fan family token may leak into ``config/webflash-builds.json``.
  * The release-notes generator does not hardcode "Release-One" wording
    for every target (the wording is product-aware).

Run with::

    python3 tests/test_all_yaml_release_matrix.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = REPO_ROOT / "products"
CLASSIFIER_PATH = REPO_ROOT / "scripts" / "classify_all_yaml_release_matrix.py"
GENERATOR_PATH = REPO_ROOT / "scripts" / "generate_webflash_release_notes.py"
BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_JSON = REPO_ROOT / "config" / "product-catalog.json"
MANUAL_JSON = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
DOC_PATH = REPO_ROOT / "docs" / "all-yaml-release-matrix.md"

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
BLOCKED_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")

# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 preview build rows (room-bundle
# previews) added alongside the published VentIQ LED preview.
ROOM_BUNDLE_PREVIEW_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
)
PREVIEW_CONFIGS_TODAY = {LED_CONFIG, *ROOM_BUNDLE_PREVIEW_CONFIGS}

ALL_CLASSES = {
    "stable-release",
    "preview-release",
    "manual-candidate-only",
    "compile-only",
    "blocked",
    "not-a-product-entrypoint",
}
RELEASE_SELECTABLE_CLASSES = {"stable-release", "preview-release"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _release_eligible_config_strings() -> list[str]:
    doc = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
    return [
        e["config_string"]
        for e in doc.get("builds", [])
        if isinstance(e, dict) and isinstance(e.get("config_string"), str)
    ]


class ClassifierShapeTests(unittest.TestCase):
    """The classifier covers every YAML in products/ exactly once."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_every_yaml_is_classified_exactly_once(self) -> None:
        on_disk = sorted(
            p.relative_to(REPO_ROOT).as_posix() for p in PRODUCTS_DIR.rglob("*.yaml")
        )
        recorded = [r["yaml_path"] for r in self.plan["records"]]
        self.assertEqual(
            sorted(recorded),
            on_disk,
            "classifier must enumerate every YAML under products/ exactly once",
        )
        # No duplicates.
        self.assertEqual(len(recorded), len(set(recorded)))

    def test_every_record_has_a_known_class(self) -> None:
        for r in self.plan["records"]:
            self.assertIn(
                r["release_class"],
                ALL_CLASSES,
                f"{r['yaml_path']} has unknown release_class {r['release_class']!r}",
            )

    def test_counts_sum_to_yaml_total(self) -> None:
        total = sum(self.plan["counts"].values())
        self.assertEqual(total, self.plan["yaml_total"])
        self.assertEqual(self.plan["yaml_total"], len(self.plan["records"]))


class ReleaseSelectableTests(unittest.TestCase):
    """Release-selectable = stable-release ∪ preview-release, from builds.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_release_selectable_matches_webflash_builds_json(self) -> None:
        from_builds = set(_release_eligible_config_strings())
        from_classifier = set(self.plan["release_selectable"])
        self.assertEqual(
            from_builds,
            from_classifier,
            "release-selectable set must equal config/webflash-builds.json — "
            "release selection must be derived from source of truth, not "
            "hardcoded to one config",
        )

    def test_only_release_selectable_classes_are_release_selectable(self) -> None:
        for r in self.plan["records"]:
            if r["is_release_selectable"]:
                self.assertIn(
                    r["release_class"],
                    RELEASE_SELECTABLE_CLASSES,
                    f"{r['yaml_path']} is_release_selectable but release_class "
                    f"is {r['release_class']!r}",
                )
            else:
                self.assertNotIn(
                    r["release_class"],
                    RELEASE_SELECTABLE_CLASSES,
                    f"{r['yaml_path']} marked not selectable but its class "
                    f"is {r['release_class']!r}",
                )

    def test_exactly_one_stable_target_today(self) -> None:
        self.assertEqual(
            self.plan["stable_targets"],
            [STABLE_CONFIG],
            "today only Ceiling-POE-VentIQ-RoomIQ is on stable",
        )

    def test_preview_targets_today(self) -> None:
        # The published VentIQ LED preview plus the three room-bundle preview
        # build rows added by RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001. Compared
        # as a set so the YAML-sorted order of the classifier is not asserted.
        self.assertEqual(
            set(self.plan["preview_targets"]),
            PREVIEW_CONFIGS_TODAY,
            "preview targets must be the VentIQ LED preview plus the three "
            "room-bundle preview build rows",
        )
        # The stable Release-One target must never appear on the preview list.
        self.assertNotIn(STABLE_CONFIG, self.plan["preview_targets"])


class LedPreviewOnlyTests(unittest.TestCase):
    """LED is preview-only and cannot be selected as stable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def _canonical_led(self) -> dict:
        canonical = [
            r
            for r in self.plan["records"]
            if r["config_string"] == LED_CONFIG
            and not r["yaml_path"].startswith("products/webflash/")
        ]
        self.assertEqual(
            len(canonical),
            1,
            "exactly one canonical (non-wrapper) LED entry expected",
        )
        return canonical[0]

    def test_led_is_classified_preview_release(self) -> None:
        led = self._canonical_led()
        self.assertEqual(led["release_class"], "preview-release")
        self.assertEqual(led["channel"], "preview")

    def test_led_is_not_in_stable_targets(self) -> None:
        self.assertNotIn(LED_CONFIG, self.plan["stable_targets"])

    def test_led_artifact_carries_preview_suffix_not_stable(self) -> None:
        led = self._canonical_led()
        artifact = (led["artifact_name"] or "").lower()
        self.assertIn("preview", artifact)
        self.assertNotIn("stable", artifact)


class FanCandidatesNotReleaseSelectableTests(unittest.TestCase):
    """FanRelay / FanPWM / FanDAC are manual-candidate-only, not releasable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_three_manual_candidates(self) -> None:
        manual = [
            r
            for r in self.plan["records"]
            if r["release_class"] == "manual-candidate-only"
        ]
        self.assertEqual(len(manual), 3, f"expected 3 manual candidates, got {manual}")

    def test_fan_candidates_are_manual_or_blocked_class(self) -> None:
        # FanRelay / FanPWM / FanDAC product configs are never release-selectable.
        # The published / manual-lane fan previews are manual-candidate-only; the
        # ROOM-BUNDLE-FAN-CONFIGS-001 compile-pending room-bundle fan previews are
        # catalog hardware-pending with no release path yet -> blocked. Neither is
        # ever stable-release / preview-release.
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            for token in FAN_TOKENS:
                if token.lower() in cs.lower():
                    self.assertIn(
                        r["release_class"],
                        {"manual-candidate-only", "blocked"},
                        f"{cs} carries {token}; must be manual-candidate-only or "
                        "blocked (never release-selectable)",
                    )

    def test_fan_candidates_are_not_release_selectable(self) -> None:
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            for token in FAN_TOKENS:
                if token.lower() in cs.lower():
                    self.assertFalse(
                        r["is_release_selectable"],
                        f"{cs} carries {token}; must not be release-selectable",
                    )

    def test_fan_candidates_have_no_artifact_name(self) -> None:
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            for token in FAN_TOKENS:
                if token.lower() in cs.lower():
                    self.assertIsNone(
                        r["artifact_name"],
                        f"{cs} must not carry an artifact_name (manual-only)",
                    )

    def test_fan_tokens_absent_from_release_matrix(self) -> None:
        for cs in _release_eligible_config_strings():
            for token in FAN_TOKENS:
                self.assertNotIn(
                    token.lower(),
                    cs.lower(),
                    f"release-matrix config {cs!r} carries fan token {token!r}",
                )

    def test_fan_tokens_absent_from_release_selectable_list(self) -> None:
        for cs in self.plan["release_selectable"]:
            for token in FAN_TOKENS:
                self.assertNotIn(
                    token.lower(),
                    cs.lower(),
                    f"release-selectable {cs!r} carries fan token {token!r}",
                )


class FanTriacBlockedTests(unittest.TestCase):
    """FanTRIAC is blocked, never selectable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_fantriac_blocked(self) -> None:
        canonical = [
            r
            for r in self.plan["records"]
            if r["config_string"] == BLOCKED_CONFIG
            and not r["yaml_path"].startswith("products/webflash/")
        ]
        self.assertEqual(
            len(canonical),
            1,
            "exactly one canonical FanTRIAC entry expected",
        )
        self.assertEqual(canonical[0]["release_class"], "blocked")
        self.assertFalse(canonical[0]["is_release_selectable"])
        self.assertIsNone(canonical[0]["artifact_name"])

    def test_fantriac_not_in_release_matrix(self) -> None:
        self.assertNotIn(BLOCKED_CONFIG, _release_eligible_config_strings())


class CompileOnlyTests(unittest.TestCase):
    """Compile-only skeletons are CI validation only, not release products."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_every_compile_only_yaml_is_compile_only_class(self) -> None:
        for r in self.plan["records"]:
            if r["yaml_path"].startswith("products/compile-only/"):
                self.assertEqual(
                    r["release_class"],
                    "compile-only",
                    f"{r['yaml_path']} under products/compile-only/ must be "
                    "classified compile-only",
                )

    def test_compile_only_yamls_are_not_release_selectable(self) -> None:
        for r in self.plan["records"]:
            if r["yaml_path"].startswith("products/compile-only/"):
                self.assertFalse(r["is_release_selectable"])
                self.assertIsNone(r["artifact_name"])


class WebflashWrappersAreNotEntrypointsTests(unittest.TestCase):
    """WebFlash wrappers re-include the canonical YAML; they are not entry points."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_every_webflash_wrapper_is_not_entrypoint(self) -> None:
        for r in self.plan["records"]:
            if r["yaml_path"].startswith("products/webflash/"):
                self.assertEqual(r["release_class"], "not-a-product-entrypoint")
                self.assertTrue(r["is_webflash_wrapper"])
                self.assertFalse(r["is_release_selectable"])


class HelperYamlsAreNotEntrypointsTests(unittest.TestCase):
    """Helper YAMLs (secrets.yaml, etc.) are not release products."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_secrets_yaml_is_not_entrypoint(self) -> None:
        secrets = [
            r for r in self.plan["records"] if r["yaml_path"] == "products/secrets.yaml"
        ]
        self.assertEqual(len(secrets), 1)
        self.assertEqual(secrets[0]["release_class"], "not-a-product-entrypoint")
        self.assertFalse(secrets[0]["is_release_selectable"])

    def test_legacy_compatible_yamls_are_not_entrypoints(self) -> None:
        catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        legacy_yamls = {
            p["product_yaml"]
            for p in catalog.get("products", [])
            if isinstance(p, dict) and p.get("status") == "legacy-compatible"
        }
        for r in self.plan["records"]:
            if r["yaml_path"] in legacy_yamls:
                self.assertEqual(
                    r["release_class"],
                    "not-a-product-entrypoint",
                    f"legacy YAML {r['yaml_path']} must be " "not-a-product-entrypoint",
                )
                self.assertFalse(r["is_release_selectable"])


class FanGuardrailTests(unittest.TestCase):
    """The fan-exclusion guardrail in the classifier matches the planner."""

    def setUp(self) -> None:
        self.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)

    def test_classifier_refuses_fan_in_release_matrix(self) -> None:
        builds = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
        manual = json.loads(MANUAL_JSON.read_text(encoding="utf-8"))
        # Inject a synthetic FanRelay row.
        bad_builds = dict(builds)
        bad_builds["builds"] = list(builds.get("builds", [])) + [
            {
                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "product_yaml": "products/webflash/ceiling-poe-ventiq-"
                "fanrelay-roomiq.yaml",
                "channel": "stable",
                "version": "1.0.0",
                "artifact_name": "Sense360-fake.bin",
                "chip_family": "ESP32-S3",
                "hardware_requirements": [],
                "features": [],
            }
        ]
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            builds_path = Path(tmpdir) / "webflash-builds.json"
            manual_path = Path(tmpdir) / "manual-firmware-artifacts.json"
            builds_path.write_text(json.dumps(bad_builds), encoding="utf-8")
            manual_path.write_text(json.dumps(manual), encoding="utf-8")
            with self.assertRaises(self.classifier.ClassifyError) as ctx:
                self.classifier.classify(
                    builds_path=builds_path,
                    manual_path=manual_path,
                )
            self.assertIn("fan", str(ctx.exception).lower())


class GeneratorWordingTests(unittest.TestCase):
    """Generated notes do not hardcode "Release-One" for every target."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = _load_module("generate_webflash_release_notes", GENERATOR_PATH)

    def test_stable_body_does_not_call_every_target_release_one(self) -> None:
        body = self.gen.generate(
            config_string=STABLE_CONFIG,
            version="1.0.0",
            channel="stable",
        )
        # Verify the body is product-aware: it must name the config string
        # explicitly. (It is acceptable for the stable RoomIQ body to
        # reference "Release-One" since that IS Release-One; what matters is
        # the LED body, below.)
        self.assertIn(STABLE_CONFIG, body)

    def test_preview_body_is_not_titled_release_one_firmware(self) -> None:
        body = self.gen.generate(
            config_string=LED_CONFIG,
            version="1.0.0",
            channel="preview",
        )
        # The wording reword from RELEASE-PRODUCT-SELECTION-001 makes the
        # LED Known-Issues bullet name the LED config and place it on the
        # preview channel — not refer to the LED firmware as "this
        # Release-One firmware".
        self.assertNotIn("this Release-One firmware", body)
        self.assertIn(LED_CONFIG, body)


class DocCoversAllSixClassesTests(unittest.TestCase):
    """The doc enumerates all six release classes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc_text = (
            DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.is_file() else ""
        )

    def test_doc_exists(self) -> None:
        self.assertTrue(
            DOC_PATH.is_file(),
            f"docs/all-yaml-release-matrix.md must exist at {DOC_PATH}",
        )

    def test_doc_names_every_release_class(self) -> None:
        for cls in ALL_CLASSES:
            self.assertIn(
                cls,
                self.doc_text,
                f"docs/all-yaml-release-matrix.md must name release class " f"{cls!r}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""STABLE-RELEASE-MATRIX-ALL-YAML-001 contract tests.

Locks in the all-YAML release matrix defined by the classifier
``scripts/classify_all_yaml_release_matrix.py`` (formerly documented in
``docs/all-yaml-release-matrix.md``, archived under DOCS-DISPOSITION-001;
see ``docs/archive-index.md``) so the broader release posture cannot
silently regress into the prior "only RoomIQ is release-aware" state.

The invariants enforced here:

  * **Every** YAML under ``products/`` (top-level, ``products/webflash/``,
    ``products/compile-only/``) is classified into exactly one of the six
    release classes (``stable-release``, ``preview-release``,
    ``manual-candidate-only``, ``compile-only``, ``blocked``,
    ``not-a-product-entrypoint``).
  * The release-selectable set (``stable-release`` ∪ ``preview-release`` ∪
    ``experimental-release``) equals the entries in
    ``config/webflash-builds.json`` — release selection is derived from the
    source of truth, not hardcoded.
  * The stable set stays exactly Release-One plus the two owner-waiver
    promotions (``Ceiling-POE-VentIQ-RoomIQ``, ``Ceiling-POE-AirIQ-RoomIQ``,
    ``Ceiling-POE-RoomIQ``) — nothing fan-flavored is ever stable.
  * The preview targets today are the two LED previews plus the six
    FanPWM / FanDAC configs added by owner decision HW-RELEASE-001
    (docs/hw-release-001.md, 2026-07-09); the experimental targets are
    FanTRIAC plus the two FanRelay room bundles. LED stays preview-only and
    is **not** selectable as stable.
  * FanRelay / FanPWM / FanDAC are release-eligible on non-stable channels
    only (HW-RELEASE-001 channel teeth: FanRelay exactly ``experimental``,
    FanPWM / FanDAC exactly ``preview``). The three top-level fan YAMLs in
    ``config/manual-firmware-artifacts.json`` are legitimately BOTH manual
    candidates (``is_manual_candidate``) and release-selectable — the
    manual lane persists as a parallel point-to-point path.
  * Every ``products/compile-only/*.yaml`` is classified ``compile-only``
    and is **not** release-selectable.
  * Helper / package YAMLs (``products/secrets.yaml``) and every WebFlash
    wrapper under ``products/webflash/`` are
    ``not-a-product-entrypoint`` and are **not** release-selectable.
  * The fan channel guardrail in ``scripts/plan_room_release_notes.py``
    is mirrored by the classifier: a fan family token in
    ``config/webflash-builds.json`` is refused on any channel other than
    the family's approved non-stable one (never ``stable``).
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
ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
LED_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
BLOCKED_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")

# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 added three room-bundle preview
# build rows alongside the published VentIQ LED preview. STABLE-PROMOTION-
# RECONCILE-001: Ceiling-POE-RoomIQ (Bedroom, v1.0.5, 2026-06-08) and
# Ceiling-POE-AirIQ-RoomIQ (Kitchen, v1.0.6, 2026-06-09) have since been
# promoted to the stable channel under owner waivers. CI-PIPELINE-CLARITY-001
# P4a then DE-LISTED Ceiling-POE-RoomIQ-LED (never built or served). Owner
# decision HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) then retired
# the bench-proof gate, re-listed Ceiling-POE-RoomIQ-LED on the preview
# channel, and added the six FanPWM / FanDAC preview rows and the two
# FanRelay experimental rows. Today's channel split is three stable targets,
# eight preview targets, and three experimental targets (FanTRIAC plus the
# two FanRelay room bundles). The stable set never gains a fan-flavored
# config.
STABLE_CONFIGS_TODAY = {
    STABLE_CONFIG,
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
}
PREVIEW_CONFIGS_TODAY = {
    LED_CONFIG,
    "Ceiling-POE-RoomIQ-LED",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
    "Ceiling-POE-FanDAC",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
}
EXPERIMENTAL_CONFIGS_TODAY = {
    BLOCKED_CONFIG,
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
}
# HW-RELEASE-001 channel teeth: the only channel each fan family may
# release on. Never "stable".
FAN_ALLOWED_CHANNELS = {
    "FanRelay": "experimental",
    "FanPWM": "preview",
    "FanDAC": "preview",
}

ALL_CLASSES = {
    "stable-release",
    "preview-release",
    # TRIAC-COMMISSIONING-001: experimental self-build mains channel
    # (config/release-channel-policy.json experimental_lane). Release-selectable
    # on the experimental channel, but never stable / recommended / default /
    # buyable / kit-exposed.
    "experimental-release",
    "manual-candidate-only",
    "compile-only",
    "blocked",
    "not-a-product-entrypoint",
}
RELEASE_SELECTABLE_CLASSES = {
    "stable-release",
    "preview-release",
    "experimental-release",
}


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

    def test_stable_targets_today(self) -> None:
        # Release-One plus the two owner-waiver promotions (Bedroom v1.0.5,
        # Kitchen v1.0.6). Compared as a set so the YAML-sorted order of the
        # classifier is not asserted.
        self.assertEqual(
            set(self.plan["stable_targets"]),
            STABLE_CONFIGS_TODAY,
            "stable targets must be Release-One plus the two promoted bundles",
        )

    def test_preview_targets_today(self) -> None:
        # HW-RELEASE-001: the published VentIQ LED preview plus the re-listed
        # Ceiling-POE-RoomIQ-LED and the six FanPWM / FanDAC configs.
        # Compared as a set so the YAML-sorted order of the classifier is
        # not asserted.
        self.assertEqual(
            set(self.plan["preview_targets"]),
            PREVIEW_CONFIGS_TODAY,
            "preview targets must be the two LED previews plus the six "
            "HW-RELEASE-001 FanPWM / FanDAC configs",
        )
        # The stable Release-One target must never appear on the preview list.
        self.assertNotIn(STABLE_CONFIG, self.plan["preview_targets"])

    def test_experimental_targets_today(self) -> None:
        # FanTRIAC (TRIAC-COMMISSIONING-001) plus the two FanRelay room
        # bundles added by HW-RELEASE-001 on the experimental channel only
        # (mains-adjacent lane per COMPLIANCE-001; never stable).
        self.assertEqual(
            set(self.plan["experimental_targets"]),
            EXPERIMENTAL_CONFIGS_TODAY,
            "experimental targets must be FanTRIAC plus the two "
            "HW-RELEASE-001 FanRelay room bundles",
        )


class LedPreviewOnlyTests(unittest.TestCase):
    """LED is preview-only and cannot be selected as stable.

    HW-RELEASE-001 re-listed Ceiling-POE-RoomIQ-LED on the preview channel
    (reversing the CI-PIPELINE-CLARITY-001 P4a de-list), so the LED preview
    set now covers both LED configs.
    """

    LED_CONFIGS = (LED_CONFIG, "Ceiling-POE-RoomIQ-LED")

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def _canonical_led(self, config_string: str) -> dict:
        canonical = [
            r
            for r in self.plan["records"]
            if r["config_string"] == config_string
            and not r["yaml_path"].startswith("products/webflash/")
        ]
        self.assertEqual(
            len(canonical),
            1,
            f"exactly one canonical (non-wrapper) entry expected for "
            f"{config_string}",
        )
        return canonical[0]

    def test_led_is_classified_preview_release(self) -> None:
        for config_string in self.LED_CONFIGS:
            led = self._canonical_led(config_string)
            self.assertEqual(led["release_class"], "preview-release")
            self.assertEqual(led["channel"], "preview")

    def test_led_is_in_preview_targets(self) -> None:
        for config_string in self.LED_CONFIGS:
            self.assertIn(config_string, self.plan["preview_targets"])

    def test_led_is_not_in_stable_targets(self) -> None:
        for config_string in self.LED_CONFIGS:
            self.assertNotIn(config_string, self.plan["stable_targets"])

    def test_led_artifact_carries_preview_suffix_not_stable(self) -> None:
        for config_string in self.LED_CONFIGS:
            led = self._canonical_led(config_string)
            artifact = (led["artifact_name"] or "").lower()
            self.assertIn("preview", artifact)
            self.assertNotIn("stable", artifact)


class FanChannelPostureTests(unittest.TestCase):
    """HW-RELEASE-001: fan configs release on non-stable channels only.

    The three top-level fan YAMLs tracked in
    config/manual-firmware-artifacts.json are legitimately BOTH manual
    candidates (parallel point-to-point lane) and release-selectable now;
    what can never happen is a fan-flavored config in the stable class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_three_manual_candidate_flags(self) -> None:
        # The manual lane still lists exactly three candidates; each now
        # also has a builds row, so the record keeps is_manual_candidate
        # True while classifying by its release channel.
        manual_doc = json.loads(MANUAL_JSON.read_text(encoding="utf-8"))
        manual_yamls = {c["product_yaml"] for c in manual_doc["candidates"]}
        self.assertEqual(len(manual_yamls), 3)
        flagged = [r for r in self.plan["records"] if r["is_manual_candidate"]]
        self.assertEqual(
            {r["yaml_path"] for r in flagged},
            manual_yamls,
            "exactly the three manual-lane YAMLs must carry is_manual_candidate",
        )

    def test_manual_candidates_dual_role(self) -> None:
        # HW-RELEASE-001: each manual candidate is also release-selectable
        # on its family's non-stable channel — the manual lane is no longer
        # the only fan path.
        for r in self.plan["records"]:
            if not r["is_manual_candidate"]:
                continue
            self.assertTrue(
                r["is_release_selectable"],
                f"{r['yaml_path']} is a manual candidate and must also be "
                "release-selectable per HW-RELEASE-001",
            )
            self.assertIn(
                r["release_class"],
                {"preview-release", "experimental-release"},
                f"{r['yaml_path']} must classify preview/experimental, never stable",
            )

    def test_fan_configs_never_stable_class(self) -> None:
        # Nothing fan-flavored is ever stable-release class.
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            for token in FAN_TOKENS:
                if token.lower() in cs.lower():
                    self.assertNotEqual(
                        r["release_class"],
                        "stable-release",
                        f"{cs} carries {token}; must never be stable-release",
                    )

    def test_release_selectable_fans_on_family_channel_only(self) -> None:
        # A release-selectable fan record must sit exactly on its family's
        # HW-RELEASE-001 channel (FanRelay: experimental; FanPWM / FanDAC:
        # preview).
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            for token, allowed in FAN_ALLOWED_CHANNELS.items():
                if token.lower() in cs.lower() and r["is_release_selectable"]:
                    self.assertEqual(
                        r["channel"],
                        allowed,
                        f"{cs} carries {token}; release channel must be "
                        f"exactly {allowed!r}",
                    )

    def test_fan_artifact_names_never_stable(self) -> None:
        # Fan configs now carry artifact names (HW-RELEASE-001), but the
        # artifact suffix must match the non-stable channel.
        for r in self.plan["records"]:
            cs = r.get("config_string") or ""
            artifact = (r["artifact_name"] or "").lower()
            for token in FAN_TOKENS:
                if token.lower() in cs.lower() and artifact:
                    self.assertNotIn(
                        "stable",
                        artifact,
                        f"{cs} artifact {artifact!r} must never be stable",
                    )

    def test_fan_rows_in_release_matrix_never_stable(self) -> None:
        # Fan tokens are allowed in config/webflash-builds.json now, but
        # only on the family's approved non-stable channel.
        builds = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))["builds"]
        for b in builds:
            cs = b.get("config_string", "")
            for token, allowed in FAN_ALLOWED_CHANNELS.items():
                if token.lower() in cs.lower():
                    self.assertEqual(
                        b.get("channel"),
                        allowed,
                        f"builds row {cs!r} carries {token}; channel must "
                        f"be exactly {allowed!r} (never stable)",
                    )

    def test_fan_tokens_absent_from_stable_targets(self) -> None:
        for cs in self.plan["stable_targets"]:
            for token in FAN_TOKENS:
                self.assertNotIn(
                    token.lower(),
                    cs.lower(),
                    f"stable target {cs!r} carries fan token {token!r}",
                )


class FanTriacBlockedTests(unittest.TestCase):
    """FanTRIAC is blocked, never release-selectable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)
        cls.plan = cls.classifier.classify()

    def test_fantriac_experimental_self_build(self) -> None:
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
        # TRIAC-COMMISSIONING-001 moved FanTRIAC into the experimental self-build
        # mains lane (config/release-channel-policy.json experimental_lane). The
        # canonical YAML now classifies as experimental-release: release-selectable
        # on the experimental channel, with the -experimental artifact. It is
        # never a stable / preview customer build (asserted below).
        self.assertEqual(canonical[0]["release_class"], "experimental-release")
        self.assertTrue(canonical[0]["is_release_selectable"])
        self.assertEqual(canonical[0]["channel"], "experimental")
        self.assertEqual(
            canonical[0]["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin",
        )

    def test_fantriac_release_eligible_experimental_only(self) -> None:
        # FanTRIAC is now release-eligible, but ONLY on the experimental channel
        # (TRIAC-COMMISSIONING-001); it is never a stable / preview customer build.
        self.assertIn(BLOCKED_CONFIG, _release_eligible_config_strings())
        builds = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))["builds"]
        triac = next(b for b in builds if b["config_string"] == BLOCKED_CONFIG)
        self.assertEqual(triac["channel"], "experimental")
        self.assertNotIn(BLOCKED_CONFIG, STABLE_CONFIGS_TODAY)
        self.assertNotIn(BLOCKED_CONFIG, PREVIEW_CONFIGS_TODAY)


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
        # SEC-ESP-SECRET-GUARD-001: products/secrets.yaml (the tracked symlink)
        # was replaced by the tracked products/secrets.example.yaml template.
        # The helper template is still not a release product entrypoint.
        secrets = [
            r
            for r in self.plan["records"]
            if r["yaml_path"] == "products/secrets.example.yaml"
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
    """The HW-RELEASE-001 fan channel guardrail matches the planner's."""

    def setUp(self) -> None:
        self.classifier = _load_module("classify_all_yaml", CLASSIFIER_PATH)

    def test_classifier_refuses_fan_on_stable_channel(self) -> None:
        builds = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
        manual = json.loads(MANUAL_JSON.read_text(encoding="utf-8"))
        # Inject a synthetic FanRelay row on the FORBIDDEN stable channel.
        # HW-RELEASE-001 allows fan rows on the family's non-stable channel
        # only (FanRelay: experimental), so a stable fan row must still be
        # refused.
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
        cls.catalog_by_cs = {
            p.get("config_string"): p
            for p in json.loads(CATALOG_JSON.read_text(encoding="utf-8"))["products"]
            if isinstance(p, dict) and p.get("config_string")
        }

    def _live_version(self, config_string: str) -> str:
        # The generator fails closed when --version disagrees with the catalog,
        # so derive the live version instead of pinning one that rots on every
        # release bump.
        return self.catalog_by_cs[config_string]["version"]

    def test_stable_body_does_not_call_every_target_release_one(self) -> None:
        body = self.gen.generate(
            config_string=STABLE_CONFIG,
            version=self._live_version(STABLE_CONFIG),
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
            version=self._live_version(LED_CONFIG),
            channel="preview",
        )
        # The wording reword from RELEASE-PRODUCT-SELECTION-001 makes the
        # LED Known-Issues bullet name the LED config and place it on the
        # preview channel — not refer to the LED firmware as "this
        # Release-One firmware".
        self.assertNotIn("this Release-One firmware", body)
        self.assertIn(LED_CONFIG, body)


class DocArchivedTests(unittest.TestCase):
    """The matrix doc was archived under DOCS-DISPOSITION-001.

    ``docs/all-yaml-release-matrix.md`` was deleted with an index row
    (its content stays recoverable from the indexed SHA); the doc-pinning
    tests went with it. The classifier contract above remains the live
    guard.
    """

    def test_doc_recorded_in_archive_index(self) -> None:
        self.assertIn(
            "docs/all-yaml-release-matrix.md",
            ARCHIVE_INDEX.read_text(encoding="utf-8"),
            "the archived matrix doc must be recorded in " "docs/archive-index.md",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""MANUAL-FIRMWARE-CI-ARTIFACTS-001 regression guards.

Locks in the non-release guarantees of the manual firmware artifact lane —
``config/manual-firmware-artifacts.json``,
``scripts/validate_manual_firmware_artifacts.py``, and
``.github/workflows/manual-firmware-artifacts.yml`` — so they cannot silently
turn into a release / WebFlash path, per
``MANUAL-FIRMWARE-ARTIFACT-POLICY-001`` (PR #619).

Run with:

    python3 tests/test_manual_firmware_artifacts.py
"""

from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "manual-firmware-artifacts.yml"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_manual_firmware_artifacts import (  # noqa: E402
    artifact_basename,
    validate,
)

FAN_YAMLS = {
    "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml",
    "products/sense360-ceiling-poe-fanpwm.yaml",
    "products/sense360-ceiling-poe-fandac.yaml",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = _load(CONFIG_PATH)
        self.catalog = _load(CATALOG_PATH)
        self.targets = _load(TARGETS_PATH)

    def test_config_validates_clean(self) -> None:
        errors = validate(self.config, self.targets, self.catalog)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_mode_is_manual_candidate(self) -> None:
        self.assertEqual(self.config["artifact_mode"], "manual-candidate")

    def test_lane_is_non_release(self) -> None:
        # Cannot set a release channel; cannot be a release / WebFlash lane.
        self.assertIs(self.config["release"], False)
        self.assertIs(self.config["webflash"], False)
        self.assertIsNone(self.config["release_channel"])

    def test_covers_exactly_the_three_fan_candidates(self) -> None:
        yamls = {c["product_yaml"] for c in self.config["candidates"]}
        self.assertEqual(yamls, FAN_YAMLS)

    def test_candidates_are_top_level_not_webflash_wrappers(self) -> None:
        for cand in self.config["candidates"]:
            py = cand["product_yaml"]
            self.assertTrue(py.startswith("products/sense360-"), py)
            self.assertFalse(py.startswith("products/webflash/"), py)


class CrossReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = _load(CONFIG_PATH)
        self.catalog_by_yaml = {
            p["product_yaml"]: p
            for p in _load(CATALOG_PATH)["products"]
            if isinstance(p, dict) and p.get("product_yaml")
        }
        self.targets_by_id = {
            t["id"]: t
            for t in _load(TARGETS_PATH)["targets"]
            if isinstance(t, dict) and t.get("id")
        }

    def test_fan_candidates_remain_webflash_build_matrix_false(self) -> None:
        for cand in self.config["candidates"]:
            entry = self.catalog_by_yaml[cand["product_yaml"]]
            self.assertIs(
                entry.get("webflash_build_matrix"),
                False,
                f"{cand['product_yaml']} webflash_build_matrix must stay false",
            )

    def test_fan_candidates_have_no_catalog_artifact_name(self) -> None:
        # The manual lane cannot use an artifact_name from the product catalog.
        for cand in self.config["candidates"]:
            entry = self.catalog_by_yaml[cand["product_yaml"]]
            self.assertFalse(
                entry.get("artifact_name"),
                f"{cand['product_yaml']} must not carry a catalog artifact_name",
            )

    def test_fan_candidates_have_no_webflash_wrapper(self) -> None:
        for cand in self.config["candidates"]:
            entry = self.catalog_by_yaml[cand["product_yaml"]]
            self.assertFalse(
                entry.get("webflash_wrapper"),
                f"{cand['product_yaml']} must not carry a webflash_wrapper",
            )

    def test_candidates_are_full_compile_validated(self) -> None:
        for cand in self.config["candidates"]:
            target = self.targets_by_id[cand["compile_only_target_id"]]
            self.assertEqual(
                target.get("compile_validation_status"), "validated-full-compile"
            )
            self.assertIs(target.get("webflash_exposure_allowed_now"), False)


class ArtifactNameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = _load(CONFIG_PATH)
        self.catalog_artifact_names = {
            p.get("artifact_name")
            for p in _load(CATALOG_PATH)["products"]
            if isinstance(p, dict) and p.get("artifact_name")
        }

    def test_name_has_required_parts(self) -> None:
        for cand in self.config["candidates"]:
            py = cand["product_yaml"]
            name = artifact_basename(py, "abcdef12")
            stem = Path(py).stem
            self.assertIn(stem, name)  # product/config name
            self.assertIn("abcdef12", name)  # reviewed commit short SHA
            self.assertIn("-manual-", name)  # manual marker
            self.assertTrue(name.endswith("-nonrelease"))  # non-release marker

    def test_name_is_not_a_release_name(self) -> None:
        for cand in self.config["candidates"]:
            name = artifact_basename(cand["product_yaml"], "abcdef12")
            self.assertIsNone(
                re.search(r"v\d+\.\d+\.\d+", name),
                f"{name} must not carry a release version",
            )
            self.assertIsNone(
                re.search(r"-(stable|preview|beta)\b", name),
                f"{name} must not carry a release channel suffix",
            )

    def test_name_differs_from_catalog_artifact_names(self) -> None:
        for cand in self.config["candidates"]:
            name = artifact_basename(cand["product_yaml"], "abcdef12") + ".bin"
            self.assertNotIn(name, self.catalog_artifact_names)

    def test_short_sha_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            artifact_basename("products/sense360-ceiling-poe-fanpwm.yaml", "nothex!")


class ValidatorRejectsMutationsTests(unittest.TestCase):
    """The validator must fail closed on any drift toward a release lane."""

    def setUp(self) -> None:
        self.config = _load(CONFIG_PATH)
        self.catalog = _load(CATALOG_PATH)
        self.targets = _load(TARGETS_PATH)

    def _expect_error(self, mutate) -> None:
        cfg = copy.deepcopy(self.config)
        mutate(cfg)
        errors = validate(cfg, self.targets, self.catalog)
        self.assertNotEqual(errors, [], "expected validation to fail but it passed")

    def test_rejects_release_channel(self) -> None:
        self._expect_error(lambda c: c.__setitem__("release_channel", "stable"))

    def test_rejects_release_true(self) -> None:
        self._expect_error(lambda c: c.__setitem__("release", True))

    def test_rejects_webflash_true(self) -> None:
        self._expect_error(lambda c: c.__setitem__("webflash", True))

    def test_rejects_wrong_mode(self) -> None:
        self._expect_error(lambda c: c.__setitem__("artifact_mode", "release"))

    def test_rejects_webflash_wrapper_path(self) -> None:
        def mutate(c):
            c["candidates"][0]["product_yaml"] = (
                "products/webflash/ceiling-poe-ventiq-fanrelay-roomiq.yaml"
            )

        self._expect_error(mutate)

    def test_rejects_catalog_artifact_name_reuse(self) -> None:
        # If a candidate's catalog entry grew a release artifact_name, validation
        # must fail (the manual lane cannot reuse a catalog release name).
        cfg = copy.deepcopy(self.config)
        catalog = copy.deepcopy(self.catalog)
        for p in catalog["products"]:
            if p.get("product_yaml") == cfg["candidates"][0]["product_yaml"]:
                p["artifact_name"] = "Sense360-FanRelay-v1.0.0-stable.bin"
        errors = validate(cfg, self.targets, catalog)
        self.assertNotEqual(errors, [])


class WorkflowShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(WORKFLOW_PATH.is_file(), f"missing {WORKFLOW_PATH}")
        self.raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.data = yaml.safe_load(self.raw)
        # Drop comment-only lines so the workflow's own narrative comments
        # (which describe what it must NOT do) don't trip raw-text guards.
        self.body = "\n".join(
            line for line in self.raw.splitlines() if line.lstrip()[:1] != "#"
        )

    def _triggers(self) -> dict:
        raw = self.data.get("on")
        if raw is None:
            raw = self.data.get(True)
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, list):
            return {k: None for k in raw}
        if isinstance(raw, str):
            return {raw: None}
        return {}

    def test_workflow_dispatch_only(self) -> None:
        triggers = self._triggers()
        self.assertEqual(
            set(triggers),
            {"workflow_dispatch"},
            "manual artifact workflow must be workflow_dispatch only "
            "(no push / pull_request / release triggers)",
        )

    def test_requires_artifact_mode_input(self) -> None:
        inputs = self._triggers()["workflow_dispatch"]["inputs"]
        self.assertIn("artifact_mode", inputs)
        mode = inputs["artifact_mode"]
        self.assertTrue(mode.get("required"))
        self.assertIn("manual-candidate", mode.get("options", []))
        # The default must NOT build anything.
        self.assertNotEqual(mode.get("default"), "manual-candidate")

    def test_jobs_gated_on_manual_candidate(self) -> None:
        # The entry job must gate on artifact_mode == manual-candidate so a
        # bare dispatch (or any other mode) builds nothing.
        self.assertIn("manual-candidate", self.raw)
        gen = self.data["jobs"]["generate-matrix"]
        self.assertIn("artifact_mode", gen.get("if", ""))
        self.assertIn("manual-candidate", gen.get("if", ""))

    def test_top_level_permissions_read_only(self) -> None:
        self.assertEqual(self.data.get("permissions"), {"contents": "read"})

    def test_no_write_permissions_anywhere(self) -> None:
        def scopes(perms):
            if isinstance(perms, dict):
                return list(perms.values())
            if isinstance(perms, str):
                return [perms]
            return []

        for value in scopes(self.data.get("permissions")):
            self.assertNotIn(value, ("write", "write-all"))
        for job in self.data.get("jobs", {}).values():
            if isinstance(job, dict):
                for value in scopes(job.get("permissions")):
                    self.assertNotIn(value, ("write", "write-all"))

    def test_does_not_create_a_github_release(self) -> None:
        # No `release` trigger (parsed), and no release-attach action.
        self.assertNotIn("release", self._triggers())
        self.assertNotIn("action-gh-release", self.body)
        self.assertNotIn("softprops/", self.body)

    def test_does_not_write_sources_or_manifest(self) -> None:
        self.assertNotIn("firmware/sources.json", self.body)
        self.assertNotIn("manifest.json", self.body)

    def test_no_checksum_generation(self) -> None:
        for token in ("sha256sum", "md5sum", "checksums-sha256", "checksums-md5"):
            self.assertNotIn(token, self.body, f"manual lane must not emit {token}")

    def test_uploads_only_expiring_artifacts(self) -> None:
        self.assertIn("actions/upload-artifact", self.body)
        self.assertIn("retention-days", self.body)
        # No download/release-attach job exists.
        self.assertNotIn("download-artifact", self.body)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""MANUAL-FIRMWARE-CI-ARTIFACTS-001 regression guards.

Locks in the non-release guarantees of the manual firmware artifact lane —
``config/manual-firmware-artifacts.json``,
``scripts/validate_manual_firmware_artifacts.py``, and
``.github/workflows/manual-firmware-artifacts.yml`` — so they cannot silently
turn into a release / WebFlash path, per
``MANUAL-FIRMWARE-ARTIFACT-POLICY-001`` (PR #619).

HW-RELEASE-001 (docs/hw-release-001.md, owner decision of record, 2026-07-09)
retired the bench-proof documentation gate and added declaration-driven
``config/webflash-builds.json`` rows for the three fan candidates, so their
``config/product-catalog.json`` entries now legitimately carry
``webflash_build_matrix: true``, a release ``artifact_name``, and a
``webflash_wrapper``. The manual lane itself is UNCHANGED and its non-release
teeth stand: workflow_dispatch-only, no GitHub Release, no manifest /
sources.json, expiring artifacts only, and manual artifact names must never
reuse a catalog release ``artifact_name``. Fan candidates' catalog channel
must never be ``stable`` (FanRelay → experimental; FanPWM / FanDAC → preview).

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
# HW-RELEASE-001: the fan candidates' catalog build channel, per lane. FanRelay
# is mains-adjacent, so experimental only; FanPWM / FanDAC are SELV previews.
# NONE may ever be "stable".
CANDIDATE_CATALOG_CHANNEL = {
    "fanrelay": "experimental",
    "fanpwm": "preview",
    "fandac": "preview",
}
HW_RELEASE_HARDWARE_STATUS = "owner-declared-bench-working-hw-release-001"

# HW-RELEASE-001 reconciliation drift the stale manual-lane validator is KNOWN
# to report until its refresh lands downstream: the catalog now legitimately
# carries webflash_build_matrix=true, an artifact_name, and a webflash_wrapper
# for the three fan candidates (declaration-driven build rows). Any error
# outside this allowance is a real regression.


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = _load(CONFIG_PATH)
        self.catalog = _load(CATALOG_PATH)
        self.targets = _load(TARGETS_PATH)

    def test_config_validates_clean(self) -> None:
        # HW-RELEASE-001 refreshed the manual-lane validator in lock-step
        # with the catalog posture (fan candidates are release-eligible on
        # non-stable channels; the manual lane still never reuses the
        # catalog release artifact_name), so the config validates clean.
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

    def test_fan_candidates_are_on_the_build_matrix_never_stable(self) -> None:
        # Inverts the pre-HW-RELEASE-001 "webflash_build_matrix must stay
        # false" pin: the owner declaration legitimately flipped the three fan
        # candidates onto the declaration-driven build matrix (status preview,
        # owner-declared hardware). The permanent tooth is the CHANNEL: a fan
        # candidate's catalog channel is experimental (FanRelay) or preview
        # (FanPWM / FanDAC) and NEVER "stable".
        for cand in self.config["candidates"]:
            with self.subTest(candidate=cand["id"]):
                entry = self.catalog_by_yaml[cand["product_yaml"]]
                self.assertIs(entry.get("webflash_build_matrix"), True)
                self.assertEqual(entry.get("status"), "preview")
                self.assertEqual(
                    entry.get("hardware_status"), HW_RELEASE_HARDWARE_STATUS
                )
                self.assertEqual(
                    entry.get("channel"),
                    CANDIDATE_CATALOG_CHANNEL[cand["id"]],
                )
                self.assertNotEqual(
                    entry.get("channel"),
                    "stable",
                    f"{cand['product_yaml']}: fan candidates are never stable",
                )

    def test_fan_candidates_catalog_artifact_name_is_release_shaped(self) -> None:
        # Inverts the pre-HW-RELEASE-001 "no catalog artifact_name" pin: the
        # catalog entries now carry the declaration-driven release artifact
        # name. It must match the channel and can never be a stable name; the
        # manual lane must still never REUSE it (ArtifactNameTests below).
        for cand in self.config["candidates"]:
            with self.subTest(candidate=cand["id"]):
                entry = self.catalog_by_yaml[cand["product_yaml"]]
                channel = CANDIDATE_CATALOG_CHANNEL[cand["id"]]
                self.assertEqual(
                    entry.get("artifact_name"),
                    f"Sense360-{entry['config_string']}-v1.0.0-{channel}.bin",
                )
                self.assertNotIn("-stable.bin", entry["artifact_name"])

    def test_fan_candidates_webflash_wrapper_exists_and_is_distinct(self) -> None:
        # Inverts the pre-HW-RELEASE-001 "no webflash_wrapper" pin: each fan
        # candidate's catalog entry now records its products/webflash wrapper.
        # The wrapper must exist on disk and the manual lane must keep building
        # the top-level product YAML, never the wrapper.
        for cand in self.config["candidates"]:
            with self.subTest(candidate=cand["id"]):
                entry = self.catalog_by_yaml[cand["product_yaml"]]
                wrapper = entry.get("webflash_wrapper")
                self.assertTrue(
                    str(wrapper).startswith("products/webflash/"),
                    f"{cand['product_yaml']}: wrapper path {wrapper!r}",
                )
                self.assertTrue((REPO_ROOT / wrapper).is_file())
                self.assertNotEqual(cand["product_yaml"], wrapper)

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
        # HW-RELEASE-001 gave the fan candidates real catalog release
        # artifact_names, so this distinctness guard now has live teeth: the
        # manual lane must never REUSE a catalog release name.
        self.assertTrue(
            self.catalog_artifact_names,
            "expected catalog release artifact_names to exist (HW-RELEASE-001)",
        )
        for cand in self.config["candidates"]:
            name = artifact_basename(cand["product_yaml"], "abcdef12") + ".bin"
            self.assertNotIn(name, self.catalog_artifact_names)

    def test_name_never_collides_with_release_name_shape(self) -> None:
        # Strengthened distinctness (HW-RELEASE-001): the manual basename can
        # never even take the release-name SHAPE the catalog now uses
        # (Sense360-{config}-v{semver}-{channel}.bin), regardless of the SHA.
        release_shape = re.compile(r"^Sense360-.*-v\d+\.\d+\.\d+-[a-z]+$")
        for cand in self.config["candidates"]:
            name = artifact_basename(cand["product_yaml"], "abcdef12")
            self.assertIsNone(
                release_shape.match(name),
                f"{name} must not be shaped like a catalog release artifact",
            )

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
        # HW-RELEASE-001: the baseline already carries the known validator
        # drift (see EXPECTED_VALIDATOR_DRIFT), so "any error" is no longer
        # proof the mutation was rejected. Require the mutation to introduce
        # NEW errors beyond the baseline set.
        baseline = set(validate(self.config, self.targets, self.catalog))
        cfg = copy.deepcopy(self.config)
        mutate(cfg)
        errors = set(validate(cfg, self.targets, self.catalog))
        self.assertTrue(
            errors - baseline,
            "expected the mutation to add validation errors but it did not",
        )

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
            c["candidates"][0][
                "product_yaml"
            ] = "products/webflash/ceiling-poe-ventiq-fanrelay-roomiq.yaml"

        self._expect_error(mutate)

    def test_catalog_artifact_names_are_never_reused_by_manual_lane(self) -> None:
        # HW-RELEASE-001: the candidates' catalog entries DO carry release
        # artifact_names now (non-stable channels). The manual lane's
        # basename must never equal any candidate's catalog release name,
        # and the refreshed validator must refuse a stable-channel catalog
        # entry for a candidate.
        catalog_by_yaml = {
            p.get("product_yaml"): p
            for p in self.catalog["products"]
            if isinstance(p, dict) and p.get("product_yaml")
        }
        for cand in self.config["candidates"]:
            with self.subTest(candidate=cand["id"]):
                entry = catalog_by_yaml[cand["product_yaml"]]
                catalog_name = entry["artifact_name"]
                manual = artifact_basename(cand["product_yaml"], "abcdef12")
                self.assertNotEqual(manual + ".bin", catalog_name)
                self.assertNotEqual(entry.get("channel"), "stable")
        mutated = copy.deepcopy(self.catalog)
        for entry in mutated["products"]:
            if entry.get("product_yaml") == self.config["candidates"][0][
                "product_yaml"
            ]:
                entry["channel"] = "stable"
        errors = validate(self.config, self.targets, mutated)
        self.assertTrue(
            errors,
            "a stable-channel catalog entry for a manual fan candidate "
            "must be refused (fan configs are never stable)",
        )


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

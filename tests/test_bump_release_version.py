#!/usr/bin/env python3
"""Unit tests for scripts/bump_release_version.py (RELEASE-BUMP-001).

Offline tests exercising the version-bump helpers against synthetic
catalog / build-matrix dicts (no network, no real-file mutation). They
lock in:

  * artifact-name computation;
  * locating and updating the right entry in each file;
  * the channel being reused from the catalog entry (never changed by a
    version bump, never taken as input);
  * minimal-change behaviour (only ``version`` + ``artifact_name`` for the
    one config move, in dict form and at the serialized-text level);
  * every fail-closed case (config absent from either file, a leading
    ``v`` on the version, a non-semver version, channel disagreement).

This module uses the stdlib ``unittest`` runner to match the no-pytest
convention used by the other validators in this repo. Run with::

    python3 tests/test_bump_release_version.py
"""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from bump_release_version import (  # noqa: E402
    BumpError,
    apply_plan,
    apply_update,
    build_plan,
    compute_artifact_name,
    dump_document,
    find_entry,
    load_document,
    main,
    resolve_channel,
    validate_version,
)

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
PREVIEW_CONFIG = "Ceiling-POE-RoomIQ-LED"


def _synthetic_catalog() -> dict:
    """A minimal product catalog with one stable and one preview entry."""
    return {
        "schema_version": 4,
        "description": "synthetic",
        "products": [
            {
                "config_string": PREVIEW_CONFIG,
                "status": "preview",
                "version": "1.0.0",
                "channel": "preview",
                "artifact_name": ("Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin"),
                "keep_me": "untouched",
            },
            {
                "config_string": STABLE_CONFIG,
                "status": "production",
                "version": "1.0.0",
                "channel": "stable",
                "artifact_name": (
                    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
                ),
                "notes": "release one",
            },
        ],
    }


def _synthetic_builds() -> dict:
    """A minimal WebFlash build matrix mirroring the synthetic catalog."""
    return {
        "schema_version": 2,
        "builds": [
            {
                "config_string": PREVIEW_CONFIG,
                "artifact_name": ("Sense360-Ceiling-POE-RoomIQ-LED-v1.0.0-preview.bin"),
                "channel": "preview",
                "version": "1.0.0",
                "features": ["room sensing", "led"],
            },
            {
                "config_string": STABLE_CONFIG,
                "artifact_name": (
                    "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
                ),
                "channel": "stable",
                "version": "1.0.0",
                "features": ["bathroom air", "room sensing"],
            },
        ],
    }


class ComputeArtifactNameTests(unittest.TestCase):
    def test_stable_form(self) -> None:
        self.assertEqual(
            compute_artifact_name(STABLE_CONFIG, "2.0.0", "stable"),
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v2.0.0-stable.bin",
        )

    def test_preview_form(self) -> None:
        self.assertEqual(
            compute_artifact_name(PREVIEW_CONFIG, "3.1.4", "preview"),
            "Sense360-Ceiling-POE-RoomIQ-LED-v3.1.4-preview.bin",
        )

    def test_embeds_version_and_channel_verbatim(self) -> None:
        name = compute_artifact_name("Ceiling-POE-AirIQ-RoomIQ", "10.20.30", "preview")
        self.assertIn("-v10.20.30-", name)
        self.assertTrue(name.endswith("-preview.bin"))


class ValidateVersionTests(unittest.TestCase):
    def test_accepts_plain_triples(self) -> None:
        for good in ("2.0.0", "1.0.0", "0.0.1", "10.20.30"):
            with self.subTest(version=good):
                validate_version(good)  # must not raise

    def test_rejects_leading_v(self) -> None:
        with self.assertRaises(BumpError) as ctx:
            validate_version("v2.0.0")
        self.assertIn("leading 'v'", str(ctx.exception))

    def test_rejects_non_semver(self) -> None:
        for bad in ("2.0", "1", "1.2.3.4", "1.0.0-rc.1", "01.0.0", "abc"):
            with self.subTest(version=bad):
                with self.assertRaises(BumpError):
                    validate_version(bad)

    def test_rejects_empty_and_whitespace(self) -> None:
        for bad in ("", "  ", " 2.0.0", "2.0.0 "):
            with self.subTest(version=repr(bad)):
                with self.assertRaises(BumpError):
                    validate_version(bad)


class FindEntryTests(unittest.TestCase):
    def test_finds_matching_entry(self) -> None:
        entries = _synthetic_catalog()["products"]
        entry = find_entry(entries, STABLE_CONFIG)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["config_string"], STABLE_CONFIG)

    def test_absent_returns_none(self) -> None:
        entries = _synthetic_catalog()["products"]
        self.assertIsNone(find_entry(entries, "No-Such-Config"))

    def test_ignores_non_dict_items(self) -> None:
        entries = ["junk", 7, {"config_string": STABLE_CONFIG}]
        self.assertEqual(
            find_entry(entries, STABLE_CONFIG)["config_string"], STABLE_CONFIG
        )


class ApplyUpdateTests(unittest.TestCase):
    def test_updates_only_version_and_artifact_name(self) -> None:
        entry = _synthetic_catalog()["products"][1]
        before_keys = list(entry.keys())
        before_channel = entry["channel"]
        before_notes = entry["notes"]

        apply_update(entry, "2.0.0", "Sense360-X-v2.0.0-stable.bin")

        self.assertEqual(entry["version"], "2.0.0")
        self.assertEqual(entry["artifact_name"], "Sense360-X-v2.0.0-stable.bin")
        # Channel and unrelated fields are untouched.
        self.assertEqual(entry["channel"], before_channel)
        self.assertEqual(entry["notes"], before_notes)
        # Key order is preserved (no keys added or reordered).
        self.assertEqual(list(entry.keys()), before_keys)


class ResolveChannelTests(unittest.TestCase):
    def test_returns_catalog_channel_when_agreeing(self) -> None:
        cat = {"channel": "stable"}
        bld = {"channel": "stable"}
        self.assertEqual(resolve_channel(cat, bld, STABLE_CONFIG), "stable")

    def test_reuses_preview_channel(self) -> None:
        cat = {"channel": "preview"}
        bld = {"channel": "preview"}
        self.assertEqual(resolve_channel(cat, bld, PREVIEW_CONFIG), "preview")

    def test_disagreement_fails_closed(self) -> None:
        cat = {"channel": "stable"}
        bld = {"channel": "preview"}
        with self.assertRaises(BumpError) as ctx:
            resolve_channel(cat, bld, STABLE_CONFIG)
        self.assertIn("channel disagreement", str(ctx.exception))

    def test_missing_channel_fails_closed(self) -> None:
        with self.assertRaises(BumpError):
            resolve_channel({}, {"channel": "stable"}, STABLE_CONFIG)
        with self.assertRaises(BumpError):
            resolve_channel({"channel": "stable"}, {}, STABLE_CONFIG)


class BuildPlanTests(unittest.TestCase):
    def test_plan_reuses_stable_channel_and_builds_artifact(self) -> None:
        plan = build_plan(
            _synthetic_catalog(), _synthetic_builds(), STABLE_CONFIG, "2.0.0"
        )
        self.assertEqual(plan.channel, "stable")
        self.assertEqual(plan.new_version, "2.0.0")
        self.assertEqual(
            plan.new_artifact_name,
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v2.0.0-stable.bin",
        )
        self.assertTrue(plan.changed)

    def test_plan_reuses_preview_channel(self) -> None:
        plan = build_plan(
            _synthetic_catalog(), _synthetic_builds(), PREVIEW_CONFIG, "2.0.0"
        )
        self.assertEqual(plan.channel, "preview")
        self.assertEqual(
            plan.new_artifact_name,
            "Sense360-Ceiling-POE-RoomIQ-LED-v2.0.0-preview.bin",
        )

    def test_plan_is_noop_when_version_unchanged(self) -> None:
        plan = build_plan(
            _synthetic_catalog(), _synthetic_builds(), STABLE_CONFIG, "1.0.0"
        )
        self.assertFalse(plan.changed)

    def test_absent_from_catalog_fails_closed(self) -> None:
        catalog = _synthetic_catalog()
        catalog["products"] = [
            p for p in catalog["products"] if p["config_string"] != STABLE_CONFIG
        ]
        with self.assertRaises(BumpError) as ctx:
            build_plan(catalog, _synthetic_builds(), STABLE_CONFIG, "2.0.0")
        self.assertIn("product catalog", str(ctx.exception))

    def test_absent_from_builds_fails_closed(self) -> None:
        builds = _synthetic_builds()
        builds["builds"] = [
            b for b in builds["builds"] if b["config_string"] != STABLE_CONFIG
        ]
        with self.assertRaises(BumpError) as ctx:
            build_plan(_synthetic_catalog(), builds, STABLE_CONFIG, "2.0.0")
        self.assertIn("build matrix", str(ctx.exception))

    def test_leading_v_fails_closed(self) -> None:
        with self.assertRaises(BumpError) as ctx:
            build_plan(
                _synthetic_catalog(), _synthetic_builds(), STABLE_CONFIG, "v2.0.0"
            )
        self.assertIn("leading 'v'", str(ctx.exception))

    def test_channel_disagreement_fails_closed(self) -> None:
        catalog = _synthetic_catalog()
        builds = _synthetic_builds()
        # Make the build matrix disagree with the catalog on channel.
        find_entry(builds["builds"], STABLE_CONFIG)["channel"] = "preview"
        with self.assertRaises(BumpError) as ctx:
            build_plan(catalog, builds, STABLE_CONFIG, "2.0.0")
        self.assertIn("channel disagreement", str(ctx.exception))


class ApplyPlanTests(unittest.TestCase):
    def test_updates_both_files_for_the_right_entry_only(self) -> None:
        catalog = _synthetic_catalog()
        builds = _synthetic_builds()
        before_catalog = copy.deepcopy(catalog)
        before_builds = copy.deepcopy(builds)

        plan = build_plan(catalog, builds, STABLE_CONFIG, "2.0.0")
        apply_plan(catalog, builds, plan)

        cat_entry = find_entry(catalog["products"], STABLE_CONFIG)
        bld_entry = find_entry(builds["builds"], STABLE_CONFIG)
        self.assertEqual(cat_entry["version"], "2.0.0")
        self.assertEqual(bld_entry["version"], "2.0.0")
        self.assertEqual(
            cat_entry["artifact_name"],
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v2.0.0-stable.bin",
        )
        self.assertEqual(bld_entry["artifact_name"], cat_entry["artifact_name"])
        # Channel is unchanged by the bump.
        self.assertEqual(cat_entry["channel"], "stable")
        self.assertEqual(bld_entry["channel"], "stable")

        # The OTHER config is byte-for-byte unchanged in both files.
        self.assertEqual(
            find_entry(catalog["products"], PREVIEW_CONFIG),
            find_entry(before_catalog["products"], PREVIEW_CONFIG),
        )
        self.assertEqual(
            find_entry(builds["builds"], PREVIEW_CONFIG),
            find_entry(before_builds["builds"], PREVIEW_CONFIG),
        )

    def test_only_two_fields_of_target_entry_change(self) -> None:
        catalog = _synthetic_catalog()
        builds = _synthetic_builds()
        before_cat = copy.deepcopy(find_entry(catalog["products"], STABLE_CONFIG))

        plan = build_plan(catalog, builds, STABLE_CONFIG, "2.0.0")
        apply_plan(catalog, builds, plan)
        after_cat = find_entry(catalog["products"], STABLE_CONFIG)

        differing = {k for k in after_cat if before_cat.get(k) != after_cat.get(k)}
        self.assertEqual(differing, {"version", "artifact_name"})


class MinimalDiffSerializationTests(unittest.TestCase):
    """The on-disk write changes only the two relevant lines per file."""

    def test_written_file_diff_is_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cat_path = Path(tmp) / "product-catalog.json"
            bld_path = Path(tmp) / "webflash-builds.json"
            dump_document(cat_path, _synthetic_catalog())
            dump_document(bld_path, _synthetic_builds())

            before_cat = cat_path.read_text(encoding="utf-8").splitlines()
            before_bld = bld_path.read_text(encoding="utf-8").splitlines()

            rc = main(
                [
                    "--config",
                    STABLE_CONFIG,
                    "--version",
                    "2.0.0",
                    "--catalog",
                    str(cat_path),
                    "--builds",
                    str(bld_path),
                    "--write",
                ]
            )
            self.assertEqual(rc, 0)

            after_cat = cat_path.read_text(encoding="utf-8").splitlines()
            after_bld = bld_path.read_text(encoding="utf-8").splitlines()

            self._assert_only_version_and_artifact_changed(before_cat, after_cat)
            self._assert_only_version_and_artifact_changed(before_bld, after_bld)

    def _assert_only_version_and_artifact_changed(self, before, after) -> None:
        self.assertEqual(len(before), len(after), "line count changed")
        changed = [(b, a) for b, a in zip(before, after) if b != a]
        self.assertEqual(len(changed), 2, f"expected 2 changed lines, got {changed}")
        joined = "\n".join(a for _, a in changed)
        self.assertIn('"version": "2.0.0"', joined)
        self.assertIn("-v2.0.0-", joined)
        self.assertIn('"version": "1.0.0"', "\n".join(b for b, _ in changed))


class DocumentIoTests(unittest.TestCase):
    def test_round_trip_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            doc = _synthetic_catalog()
            dump_document(path, doc)
            self.assertEqual(load_document(path), doc)
            # Canonical 2-space form with trailing newline.
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            self.assertIn('\n  "products": [', text)

    def test_missing_file_fails_closed(self) -> None:
        with self.assertRaises(BumpError):
            load_document(Path("/nonexistent/does-not-exist.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

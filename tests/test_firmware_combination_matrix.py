#!/usr/bin/env python3
"""Tests for the firmware combination readiness matrix.

Covers the generator at ``scripts/generate_firmware_matrix.py`` and the
on-disk matrix at ``config/firmware-combination-matrix.json``. The matrix
is readiness tracking only; these tests pin the grammar invariants and
the classification of the two committed WebFlash builds (Release-One
stable and the LED preview).

Uses Python's stdlib unittest (matching this repo's no-pytest convention
for Python validators). Run with::

    python3 tests/test_firmware_combination_matrix.py

or::

    python3 -m unittest tests.test_firmware_combination_matrix -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_firmware_matrix as gfm  # noqa: E402

COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
MATRIX_PATH = REPO_ROOT / "config" / "firmware-combination-matrix.json"

RELEASE_ONE_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ"
LED_PREVIEW_CONFIG_STRING = "Ceiling-POE-VentIQ-RoomIQ-LED"
FANTRIAC_BLOCKED_CONFIG_STRING = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"


def _load(path: Path):
    return json.loads(path.read_text())


class FirmwareMatrixGeneratorTests(unittest.TestCase):
    """Tests against the freshly-regenerated matrix.

    Regenerating in-test keeps the assertions independent of whether the
    committed file is stale; a separate test below pins file-on-disk
    freshness.
    """

    @classmethod
    def setUpClass(cls):
        cls.compat = _load(COMPAT_PATH)
        cls.builds = _load(BUILDS_PATH)
        cls.catalog = _load(CATALOG_PATH)
        cls.doc = gfm.generate(cls.compat, cls.builds, cls.catalog)
        cls.rows = cls.doc["combinations"]
        cls.by_config = {row["config_string"]: row for row in cls.rows}

    # ------------------------------------------------------------------
    # Schema / shape
    # ------------------------------------------------------------------

    def test_schema_version_is_one(self):
        self.assertEqual(self.doc["schema_version"], 1)

    def test_sources_point_to_canonical_files(self):
        self.assertEqual(
            self.doc["sources"]["compatibility"],
            "config/webflash-compatibility.json",
        )
        self.assertEqual(self.doc["sources"]["builds"], "config/webflash-builds.json")
        self.assertEqual(self.doc["sources"]["catalog"], "config/product-catalog.json")

    def test_combinations_have_required_fields(self):
        required = {
            "config_string",
            "tokens",
            "mounting",
            "power",
            "air_quality",
            "room_sense",
            "fan",
            "led",
            "status",
        }
        for row in self.rows:
            missing = required - set(row.keys())
            self.assertFalse(
                missing,
                f"row {row.get('config_string')!r} missing fields {missing}",
            )

    def test_total_count_matches_totals(self):
        self.assertEqual(self.doc["totals"]["combinations"], len(self.rows))

    def test_every_status_is_allowed(self):
        allowed = set(gfm.ALLOWED_STATUSES)
        for row in self.rows:
            self.assertIn(
                row["status"],
                allowed,
                f"unexpected status {row['status']!r} on {row['config_string']!r}",
            )

    # ------------------------------------------------------------------
    # Existing WebFlash builds
    # ------------------------------------------------------------------

    def _builds_artifact(self, config_string):
        # The matrix mirrors config/webflash-builds.json; derive the expected
        # artifact from the ledger so version bumps do not rot this test.
        for entry in self.builds.get("builds", []) or []:
            if entry.get("config_string") == config_string:
                return entry.get("artifact_name")
        self.fail(f"{config_string!r} not in config/webflash-builds.json")

    def test_release_one_stable_is_webflash_shipping(self):
        row = self.by_config[RELEASE_ONE_CONFIG_STRING]
        self.assertEqual(row["status"], "webflash-shipping")
        self.assertEqual(
            row.get("artifact_name"),
            self._builds_artifact(RELEASE_ONE_CONFIG_STRING),
        )
        self.assertTrue(row.get("artifact_name", "").endswith("-stable.bin"))

    def test_led_preview_is_webflash_preview(self):
        row = self.by_config[LED_PREVIEW_CONFIG_STRING]
        self.assertEqual(row["status"], "webflash-preview")
        self.assertEqual(
            row.get("artifact_name"),
            self._builds_artifact(LED_PREVIEW_CONFIG_STRING),
        )
        self.assertTrue(row.get("artifact_name", "").endswith("-preview.bin"))

    def test_promoted_room_bundles_match_declared_channels(self):
        # STABLE-PROMOTION-RECONCILE-001 promoted Bedroom (v1.0.5) to the
        # stable channel under an owner waiver, so the matrix must classify
        # it webflash-shipping with a stable artifact. Kitchen
        # (Ceiling-POE-AirIQ-RoomIQ) was subsequently kept on the preview
        # channel (PR #834, "Keep AirIQ RoomIQ build on preview channel":
        # the owner waiver is not hardware verification and must not cut a
        # stable build), so the matrix must classify it webflash-preview
        # with a preview artifact. Both rows mirror the authoritative
        # channel in config/webflash-builds.json.
        bedroom = self.by_config["Ceiling-POE-RoomIQ"]
        self.assertEqual(bedroom["status"], "webflash-shipping")
        self.assertEqual(
            bedroom.get("artifact_name"),
            self._builds_artifact("Ceiling-POE-RoomIQ"),
        )
        self.assertTrue(bedroom.get("artifact_name", "").endswith("-stable.bin"))

        kitchen = self.by_config["Ceiling-POE-AirIQ-RoomIQ"]
        self.assertEqual(kitchen["status"], "webflash-preview")
        self.assertEqual(
            kitchen.get("artifact_name"),
            self._builds_artifact("Ceiling-POE-AirIQ-RoomIQ"),
        )
        self.assertTrue(kitchen.get("artifact_name", "").endswith("-preview.bin"))

    def test_every_webflash_build_appears_in_matrix(self):
        builds = self.builds.get("builds", []) or []
        for entry in builds:
            cs = entry["config_string"]
            self.assertIn(
                cs,
                self.by_config,
                f"webflash-builds entry {cs!r} missing from matrix",
            )

    def test_fantriac_full_composition_is_classified_webflash_experimental(self):
        # TRIAC-COMMISSIONING-001 moved the full-composition
        # Ceiling-POE-VentIQ-FanTRIAC-RoomIQ catalog entry into the experimental
        # self-build mains lane (status preview, channel experimental, with a
        # config/webflash-builds.json row). The coarse matrix classifier maps
        # the experimental channel to the webflash-preview class ("never invents
        # new statuses"); the row's notes + artifact name carry the real
        # experimental channel and the row resolves through the products/webflash
        # wrapper. (Other FanTRIAC family combinations with no catalog entry stay
        # blocked-hardware via the family fallback.)
        row = self.by_config[FANTRIAC_BLOCKED_CONFIG_STRING]
        self.assertEqual(row["status"], "webflash-preview")
        self.assertIn("experimental", row.get("notes", ""))
        self.assertEqual(
            row.get("artifact_name"),
            "Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ-v1.0.0-experimental.bin",
        )
        self.assertEqual(
            row.get("product_yaml"),
            "products/webflash/ceiling-poe-ventiq-fantriac-roomiq.yaml",
        )

    # ------------------------------------------------------------------
    # Grammar guards
    # ------------------------------------------------------------------

    def test_no_airiq_plus_ventiq_combinations(self):
        for row in self.rows:
            tokens = row["tokens"]
            self.assertFalse(
                "AirIQ" in tokens and "VentIQ" in tokens,
                f"matrix emitted forbidden AirIQ+VentIQ combo {row['config_string']!r}",
            )

    def test_no_fandac_plus_airiq_combinations(self):
        # HW-RELEASE-001: config strings enumerated in the compat snapshot's
        # fandac_air_quality_address_policy.address_overridden_exception_
        # config_strings are the documented address-overridden exceptions
        # (IC2 relocated 0x59 -> 0x5A); every other AirIQ+FanDAC combo stays
        # forbidden by the one-click grammar mutex.
        exceptions = set(
            self.compat.get("fandac_air_quality_address_policy", {}).get(
                "address_overridden_exception_config_strings", []
            )
        )
        self.assertEqual(exceptions, {"Ceiling-POE-AirIQ-FanDAC-RoomIQ"})
        for row in self.rows:
            tokens = row["tokens"]
            if row["config_string"] in exceptions:
                continue
            self.assertFalse(
                "AirIQ" in tokens and "FanDAC" in tokens,
                f"matrix emitted forbidden FanDAC+AirIQ combo {row['config_string']!r}",
            )

    def test_no_generic_fan_token(self):
        for row in self.rows:
            tokens = row["tokens"]
            self.assertNotIn(
                "Fan",
                tokens,
                f"matrix emitted generic 'Fan' token in {row['config_string']!r}",
            )

    def test_no_forbidden_legacy_tokens(self):
        forbidden = set(self.compat.get("forbidden_tokens", []))
        for row in self.rows:
            for token in row["tokens"]:
                self.assertNotIn(
                    token,
                    forbidden,
                    f"matrix emitted forbidden token {token!r} in "
                    f"{row['config_string']!r}",
                )

    def test_at_most_one_fan_driver_token(self):
        fan_set = set(gfm.FAN_DRIVER_TOKENS)
        for row in self.rows:
            fans = [t for t in row["tokens"] if t in fan_set]
            self.assertLessEqual(
                len(fans),
                1,
                f"matrix emitted multiple fan drivers in {row['config_string']!r}: {fans}",
            )

    def test_every_combination_conforms_to_compatibility_grammar(self):
        mountings = set(self.compat["canonical_mounting"])
        powers = set(self.compat["canonical_power"])
        modules = set(self.compat["canonical_modules"])
        forbidden = set(self.compat["forbidden_tokens"])

        for row in self.rows:
            tokens = row["tokens"]
            self.assertGreaterEqual(
                len(tokens),
                2,
                f"{row['config_string']!r}: must have mounting + power",
            )
            self.assertIn(tokens[0], mountings, row["config_string"])
            self.assertIn(tokens[1], powers, row["config_string"])
            for token in tokens[2:]:
                self.assertIn(
                    token,
                    modules,
                    f"{row['config_string']!r}: unknown module token {token!r}",
                )
                self.assertNotIn(
                    token,
                    forbidden,
                    f"{row['config_string']!r}: forbidden token {token!r}",
                )

    def test_config_string_round_trips_through_tokens(self):
        for row in self.rows:
            self.assertEqual(
                "-".join(row["tokens"]),
                row["config_string"],
                f"tokens vs config_string mismatch for {row['config_string']!r}",
            )

    def test_module_order_is_canonical(self):
        """Module order must follow the §5 ordering from docs/webflash-contract.md:

        ``{Mounting}-{Power}-[AirIQ|VentIQ]-[FanRelay|FanPWM|FanDAC|FanTRIAC]-[RoomIQ]-[LED]``
        """
        air_set = {"AirIQ", "VentIQ"}
        fan_set = set(gfm.FAN_DRIVER_TOKENS)
        for row in self.rows:
            tokens = row["tokens"]
            modules = tokens[2:]

            slot_index = {
                "air": next((i for i, t in enumerate(modules) if t in air_set), None),
                "fan": next((i for i, t in enumerate(modules) if t in fan_set), None),
                "room": next((i for i, t in enumerate(modules) if t == "RoomIQ"), None),
                "led": next((i for i, t in enumerate(modules) if t == "LED"), None),
            }

            ordered = [
                (name, idx) for name, idx in slot_index.items() if idx is not None
            ]
            for (_, a), (_, b) in zip(ordered, ordered[1:]):
                self.assertLess(
                    a,
                    b,
                    f"{row['config_string']!r}: module slot order broken",
                )

    # ------------------------------------------------------------------
    # Enumeration completeness
    # ------------------------------------------------------------------

    def test_expected_combination_count(self):
        # 1 mounting * 3 powers * 3 air (none/AirIQ/VentIQ) * 5 fan
        # (none + 4 drivers) * 2 room * 2 led = 180.
        # Minus AirIQ+FanDAC combinations: 1 * 3 * 1 * 1 * 2 * 2 = 12.
        # Plus the HW-RELEASE-001 documented address-overridden exception
        # (Ceiling-POE-AirIQ-FanDAC-RoomIQ) re-admitted to the grammar = 1.
        # Net = 169.
        self.assertEqual(len(self.rows), 169)

    def test_config_strings_are_unique(self):
        seen = [row["config_string"] for row in self.rows]
        self.assertEqual(len(seen), len(set(seen)))

    def test_combinations_are_sorted(self):
        seen = [row["config_string"] for row in self.rows]
        self.assertEqual(seen, sorted(seen))

    # ------------------------------------------------------------------
    # Negative guard: invariants the matrix MUST never violate
    # ------------------------------------------------------------------

    def test_only_committed_builds_are_webflash_status(self):
        webflash_statuses = {"webflash-shipping", "webflash-preview"}
        committed = {
            entry["config_string"] for entry in self.builds.get("builds", []) or []
        }
        for row in self.rows:
            if row["status"] in webflash_statuses:
                self.assertIn(
                    row["config_string"],
                    committed,
                    f"{row['config_string']!r} marked {row['status']} but not in "
                    "config/webflash-builds.json",
                )

    def test_release_one_required_configs_all_present(self):
        required = self.compat.get("release_one_required_configs", []) or []
        for cs in required:
            self.assertIn(
                cs,
                self.by_config,
                f"Release-One required config {cs!r} missing from matrix",
            )


class FirmwareMatrixOnDiskTests(unittest.TestCase):
    """Pin the committed config/firmware-combination-matrix.json to the generator."""

    def test_committed_matrix_matches_regeneration(self):
        compat = _load(COMPAT_PATH)
        builds = _load(BUILDS_PATH)
        catalog = _load(CATALOG_PATH)
        regenerated = gfm.generate(compat, builds, catalog)
        on_disk = _load(MATRIX_PATH)
        self.assertEqual(
            on_disk,
            regenerated,
            "config/firmware-combination-matrix.json is stale; run "
            "`python3 scripts/generate_firmware_matrix.py`.",
        )


class FirmwareMatrixCLITests(unittest.TestCase):
    """The generator CLI surface."""

    def test_check_mode_passes_when_committed(self):
        rc = gfm.main(["--check"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

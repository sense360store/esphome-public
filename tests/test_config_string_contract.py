#!/usr/bin/env python3
"""Canonical firmware-configuration contract (SENSE360-CANONICALISATION-001 PR 06).

The contract answers one question per declared config string: which boards
does it compose, and which lane does it occupy? These tests are what make
the answer enforced rather than merely written down.

They pin four things:

- **Exhaustiveness.** Every hardware-layer package is bound to a board SKU
  or explicitly to none with a recorded reason, so a new package cannot
  enter the tree unclassified and an alias cannot quietly start claiming a
  board of its own.
- **One composition per config string.** Each configuration resolves to
  exactly one board composition, no two configurations resolve to the same
  one, and every SKU named exists in the hardware catalogue.
- **Catalogue agreement.** The hand-authored declarations that describe a
  configuration's hardware (``webflash-builds`` hardware requirements and
  ``core-framework`` capabilities) must agree with the composition the
  include graph actually resolves. Where they disagree, one of them is
  wrong, and the disagreement is a failure rather than a footnote.
- **Standing gates.** Release-One stays the stable room baseline, FanTRIAC
  stays in the advanced / manual lane, and no fan configuration reaches the
  stable channel.

Evidence ceiling: static inspection of declarations and the YAML include
graph. A resolved composition is a compile-time composition fact. It is
never hardware, bench, compliance, safety or commercial-availability proof,
and it never claims a connector-attached sensor is supplied.

Stdlib unittest only; runnable directly or under pytest.
"""

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_config_string_contract as gen  # noqa: E402

CONFIG_DIR = REPO_ROOT / "config"
BINDINGS_PATH = CONFIG_DIR / "board-package-bindings.json"
CONTRACT_PATH = CONFIG_DIR / "config-string-contract.json"
HARDWARE_CATALOG_PATH = CONFIG_DIR / "hardware-catalog.json"
FEATURE_MATRIX_PATH = CONFIG_DIR / "feature-entity-matrix.json"
CORE_FRAMEWORK_PATH = CONFIG_DIR / "core-framework.json"
BUILDS_PATH = CONFIG_DIR / "webflash-builds.json"
CATALOG_PATH = CONFIG_DIR / "product-catalog.json"

BOARD_SKU_RE = re.compile(r"^S360-[0-9]{3}$")
BOARD_FILENAME_RE = re.compile(r"^(s360-[0-9]{3})[-.]")

# The one configuration whose config string is outside the canonical grammar
# and is deliberately still present. The SOT charter's
# architecture_freeze.baselines.upstream_token_classifications records the
# Blower token as resolved_by_pr PR-12 ("remove obsolete blower and fan
# wrappers with no valid consumer"), so PR 06 classifies it and PR 12
# deletes it. Removing it here would resolve a token the charter assigned to
# a later PR; leaving it unrecorded would let a second one slip in beside
# it. The exemption is therefore exact and closed.
GRAMMAR_EXEMPTIONS = {
    "Ceiling-Core-AirIQ-Blower": "PR-12 (charter upstream_token_classifications: Blower)",
}

RELEASE_ONE = "Ceiling-POE-VentIQ-RoomIQ"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


class BindingExhaustivenessTests(unittest.TestCase):
    """Every hardware-layer package is classified exactly once."""

    @classmethod
    def setUpClass(cls):
        cls.doc = load(BINDINGS_PATH)
        cls.bindings = cls.doc["bindings"]
        cls.by_package = {row["package"]: row for row in cls.bindings}
        cls.catalog_skus = {
            item["sku"] for item in load(HARDWARE_CATALOG_PATH)["items"]
        }

    def test_every_hardware_layer_package_is_bound(self):
        on_disk = set()
        for directory in self.doc["hardware_layer_directories"]:
            for path in (REPO_ROOT / directory).glob("*.yaml"):
                on_disk.add(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(
            on_disk - set(self.by_package),
            set(),
            "packages exist with no binding; add them to "
            "config/board-package-bindings.json",
        )

    def test_no_binding_names_a_missing_file(self):
        for package in self.by_package:
            self.assertTrue(
                (REPO_ROOT / package).is_file(),
                f"binding names a file that does not exist: {package}",
            )

    def test_no_package_is_bound_twice(self):
        packages = [row["package"] for row in self.bindings]
        self.assertEqual(len(packages), len(set(packages)))

    def test_every_bound_sku_exists_in_the_hardware_catalogue(self):
        """This file never mints a board identity; the catalogue owns it."""
        for row in self.bindings:
            sku = row.get("board_sku")
            if sku is None:
                continue
            self.assertRegex(sku, BOARD_SKU_RE, row["package"])
            self.assertIn(sku, self.catalog_skus, row["package"])

    def test_a_board_package_never_binds_to_a_different_sku(self):
        """packages/boards/s360-NNN-*.yaml is S360-NNN or nothing, never S360-MMM."""
        for row in self.bindings:
            package = row["package"]
            if not package.startswith("packages/boards/"):
                continue
            match = BOARD_FILENAME_RE.match(Path(package).name)
            self.assertIsNotNone(match, package)
            expected = match.group(1).upper()
            sku = row.get("board_sku")
            if sku is not None:
                self.assertEqual(sku, expected, package)

    def test_every_binding_records_a_known_basis_and_a_reason(self):
        known = set(self.doc["bases"])
        for row in self.bindings:
            self.assertIn(row["basis"], known, row["package"])
            self.assertTrue(row["reason"].strip(), row["package"])

    def test_unbound_packages_are_a_decision_not_a_gap(self):
        """A null binding must never be the 'holds this board's firmware' basis."""
        for row in self.bindings:
            if row.get("board_sku") is None:
                self.assertNotEqual(
                    row["basis"],
                    "authoritative-board-firmware",
                    f"{row['package']} claims to hold board firmware but names no SKU",
                )

    def test_totals_match_the_bindings(self):
        totals = self.doc["totals"]
        self.assertEqual(totals["packages"], len(self.bindings))
        self.assertEqual(
            totals["bound"],
            sum(1 for row in self.bindings if row.get("board_sku")),
        )
        self.assertEqual(
            totals["unbound"],
            sum(1 for row in self.bindings if not row.get("board_sku")),
        )

    def test_the_feature_matrix_canonical_board_package_agrees(self):
        """The audit matrix may not contradict the enforced binding.

        feature-entity-matrix.json is planning and audit only, so it is not
        an enforcement input; but a canonical_board_package it names must
        still resolve to that SKU, either directly or through the parts it
        composes.
        """
        matrix = load(FEATURE_MATRIX_PATH)
        for board in matrix["boards"]:
            package = board.get("canonical_board_package")
            if not package:
                continue
            self.assertIn(package, self.by_package, package)
            candidates = [package] + list(board.get("composed_of") or [])
            resolved = {
                self.by_package[c].get("board_sku")
                for c in candidates
                if c in self.by_package
            }
            self.assertIn(
                board["sku"],
                resolved,
                f"{package} is declared canonical for {board['sku']} but neither "
                "it nor its composed_of parts bind to that SKU",
            )

    def test_every_capability_maps_to_a_real_board_or_explicitly_to_none(self):
        mapping = self.doc["capability_board_map"]["map"]
        declared = set(load(CORE_FRAMEWORK_PATH)["capabilities"])
        self.assertEqual(set(mapping), declared)
        for capability, sku in mapping.items():
            if sku is None:
                self.assertIn(
                    capability,
                    self.doc["capability_board_map"]["notes"],
                    f"{capability} maps to no board and must record why",
                )
            else:
                self.assertIn(sku, self.catalog_skus, capability)


class ContractFreshnessTests(unittest.TestCase):
    def test_the_generated_contract_is_up_to_date(self):
        self.assertEqual(
            gen.main(["--check"]),
            0,
            "config/config-string-contract.json is stale; run "
            "`python3 scripts/generate_config_string_contract.py`",
        )


class CompositionTests(unittest.TestCase):
    """One config string maps to exactly one board composition."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load(CONTRACT_PATH)
        cls.configurations = cls.contract["configurations"]
        cls.by_cs = {row["config_string"]: row for row in cls.configurations}
        cls.catalog_skus = {
            item["sku"] for item in load(HARDWARE_CATALOG_PATH)["items"]
        }

    def test_every_configuration_resolves_a_composition(self):
        for row in self.configurations:
            if row["classification"] == "removed":
                continue
            self.assertTrue(
                row["board_composition"],
                f"{row['config_string']} resolves no boards at all",
            )

    def test_no_two_config_strings_share_a_composition(self):
        """A duplicate composition means two identifiers for one product."""
        seen = {}
        for row in self.configurations:
            key = tuple(row["board_composition"])
            if not key:
                continue
            self.assertNotIn(
                key,
                seen,
                f"{row['config_string']} and {seen.get(key)} resolve to the "
                f"identical composition {list(key)}",
            )
            seen[key] = row["config_string"]

    def test_every_composed_sku_exists_in_the_hardware_catalogue(self):
        for row in self.configurations:
            for sku in row["board_composition"]:
                self.assertIn(sku, self.catalog_skus, row["config_string"])

    def test_no_configuration_has_an_unresolved_include(self):
        for row in self.configurations:
            self.assertEqual(row["unresolved_includes"], [], row["config_string"])

    def test_every_composition_is_sorted_and_deduplicated(self):
        for row in self.configurations:
            composition = row["board_composition"]
            self.assertEqual(composition, sorted(set(composition)))

    def test_every_configuration_composes_the_core(self):
        """Every flashable device is an S360-100 Core; nothing may omit it."""
        for row in self.configurations:
            if row["classification"] == "removed":
                continue
            self.assertIn(
                "S360-100",
                row["board_composition"],
                f"{row['config_string']} composes no Core board",
            )

    def test_canonical_yaml_exists_for_every_live_configuration(self):
        for row in self.configurations:
            if row["classification"] == "removed":
                continue
            self.assertIsNotNone(row["canonical_yaml"], row["config_string"])
            self.assertTrue(
                (REPO_ROOT / row["canonical_yaml"]).is_file(),
                row["config_string"],
            )


class GrammarTests(unittest.TestCase):
    """Every config string is a legal identifier, or a recorded exemption."""

    @classmethod
    def setUpClass(cls):
        cls.configurations = load(CONTRACT_PATH)["configurations"]

    def test_every_config_string_matches_the_sot_identifier_schema(self):
        for row in self.configurations:
            if row["config_string"] in GRAMMAR_EXEMPTIONS:
                continue
            self.assertTrue(row["grammar"]["matches_sot_schema"], row["config_string"])

    def test_no_config_string_carries_an_unknown_token(self):
        for row in self.configurations:
            if row["config_string"] in GRAMMAR_EXEMPTIONS:
                continue
            self.assertEqual(row["grammar"]["unknown_tokens"], [], row["config_string"])

    def test_the_exemption_list_is_exactly_the_recorded_debt(self):
        """A second impossible config string cannot hide beside the first."""
        invalid = {
            row["config_string"]
            for row in self.configurations
            if not row["grammar"]["valid"]
        }
        self.assertEqual(invalid, set(GRAMMAR_EXEMPTIONS))

    def test_the_generic_fan_token_is_never_used(self):
        for row in self.configurations:
            self.assertNotIn("Fan", row["grammar"]["tokens"], row["config_string"])


class ClassificationTests(unittest.TestCase):
    """Every configuration occupies exactly one of the six declared lanes."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load(CONTRACT_PATH)
        cls.configurations = cls.contract["configurations"]
        cls.by_cs = {row["config_string"]: row for row in cls.configurations}

    def test_the_six_lanes_are_declared_with_a_derivation_rule(self):
        lanes = self.contract["classification_lanes"]
        self.assertEqual(
            set(lanes),
            {"room", "advanced", "preview", "experimental", "compile-only", "removed"},
        )
        for lane, rule in lanes.items():
            self.assertTrue(rule.strip(), lane)

    def test_every_configuration_is_in_exactly_one_declared_lane(self):
        lanes = set(self.contract["classification_lanes"])
        for row in self.configurations:
            self.assertIn(row["classification"], lanes, row["config_string"])

    def test_the_totals_match_the_rows(self):
        counts = {}
        for row in self.configurations:
            counts[row["classification"]] = counts.get(row["classification"], 0) + 1
        counts["removed"] = counts.get("removed", 0) + len(self.contract["tombstones"])
        self.assertEqual(self.contract["totals"]["by_classification"], counts)
        self.assertEqual(
            self.contract["totals"]["configurations"], len(self.configurations)
        )

    def test_every_lane_is_populated(self):
        """An empty lane means the derivation rule stopped describing the tree."""
        for lane, count in self.contract["totals"]["by_classification"].items():
            self.assertGreater(count, 0, f"lane {lane} is empty")

    def test_a_room_configuration_names_the_bundles_it_serves(self):
        for row in self.configurations:
            if row["classification"] == "room":
                self.assertTrue(row["room_bundle_skus"], row["config_string"])

    def test_a_removed_tombstone_reserves_its_legacy_identifier(self):
        for row in self.contract["tombstones"]:
            self.assertTrue(row["legacy_config_id"], row)
            self.assertEqual(row["classification"], "removed")


class CatalogueReconciliationTests(unittest.TestCase):
    """The hand-authored hardware declarations must match the resolved graph."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load(CONTRACT_PATH)
        cls.by_cs = {
            row["config_string"]: row for row in cls.contract["configurations"]
        }
        cls.bindings = load(BINDINGS_PATH)
        cls.catalog_items = load(HARDWARE_CATALOG_PATH)["items"]

    def _requirement_sku(self, requirement):
        """Resolve one prose hardware requirement to a board SKU.

        An explicit SKU in the string wins; otherwise the catalogue friendly
        name is matched. Returning None means the requirement names no board,
        which the caller treats as a failure.
        """
        explicit = re.search(r"S360-[0-9]{3}", requirement)
        if explicit:
            return explicit.group(0)
        matches = [
            item["sku"]
            for item in self.catalog_items
            if item["friendly_name"] in requirement
        ]
        # Prefer the longest friendly name so "Sense360 PoE PSU" never loses
        # to a shorter prefix match.
        if matches:
            return max(
                matches,
                key=lambda sku: len(
                    next(
                        i["friendly_name"]
                        for i in self.catalog_items
                        if i["sku"] == sku
                    )
                ),
            )
        return None

    def test_declared_hardware_requirements_match_the_resolved_composition(self):
        for row in self.contract["configurations"]:
            declared = row.get("declared_hardware_requirements")
            if declared is None:
                continue
            skus = set()
            for requirement in declared:
                sku = self._requirement_sku(requirement)
                self.assertIsNotNone(
                    sku,
                    f"{row['config_string']}: hardware requirement names no "
                    f"catalogued board: {requirement!r}",
                )
                skus.add(sku)
            self.assertEqual(
                skus,
                set(row["board_composition"]),
                f"{row['config_string']}: config/webflash-builds.json hardware "
                "requirements disagree with the resolved board composition",
            )

    def test_declared_capabilities_match_the_resolved_composition(self):
        mapping = self.bindings["capability_board_map"]["map"]
        for config_string, entry in load(CORE_FRAMEWORK_PATH)["configs"].items():
            row = self.by_cs.get(config_string)
            self.assertIsNotNone(
                row,
                f"config/core-framework.json declares {config_string}, which is "
                "not a configuration in the contract",
            )
            expected = {
                mapping[capability]
                for capability in entry["capabilities"]
                if mapping.get(capability)
            }
            self.assertEqual(
                expected,
                set(row["board_composition"]),
                f"{config_string}: declared capabilities disagree with the "
                "resolved board composition",
            )

    def test_every_build_row_has_a_catalogue_entry(self):
        catalog = {
            entry["config_string"]
            for entry in load(CATALOG_PATH)["products"]
            if entry.get("config_string")
        }
        for build in load(BUILDS_PATH)["builds"]:
            self.assertIn(build["config_string"], catalog)

    def test_every_configuration_is_declared_somewhere(self):
        for row in self.contract["configurations"]:
            self.assertTrue(row["declared_in"], row["config_string"])

    def test_the_artifact_name_matches_the_config_string_and_channel(self):
        for row in self.contract["configurations"]:
            artifact = row.get("artifact_name")
            if not artifact:
                continue
            self.assertEqual(
                artifact,
                f"Sense360-{row['config_string']}-v{row['version']}-"
                f"{row['channel']}.bin",
                row["config_string"],
            )


class StandingGateTests(unittest.TestCase):
    """The contract must never be able to weaken a standing gate."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load(CONTRACT_PATH)
        cls.by_cs = {
            row["config_string"]: row for row in cls.contract["configurations"]
        }

    def test_release_one_is_the_stable_room_baseline(self):
        row = self.by_cs[RELEASE_ONE]
        self.assertEqual(row["classification"], "room")
        self.assertEqual(row["channel"], "stable")
        self.assertEqual(
            row["board_composition"],
            ["S360-100", "S360-200", "S360-211", "S360-410"],
        )

    def test_no_fan_configuration_reaches_the_stable_channel(self):
        for row in self.contract["configurations"]:
            if any(token in row["config_string"] for token in FAN_TOKENS):
                self.assertNotEqual(row["channel"], "stable", row["config_string"])
                self.assertNotEqual(row["classification"], "room", row["config_string"])

    def test_fantriac_stays_in_the_advanced_manual_lane(self):
        row = self.by_cs["Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"]
        self.assertEqual(row["classification"], "advanced")
        self.assertNotEqual(row["channel"], "stable")
        self.assertEqual(row["room_bundle_skus"], [])

    def test_no_room_configuration_is_outside_the_stable_channel(self):
        for row in self.contract["configurations"]:
            if row["classification"] == "room":
                self.assertEqual(row["channel"], "stable", row["config_string"])

    def test_the_contract_states_its_evidence_ceiling(self):
        ceiling = self.contract["evidence_ceiling"].lower()
        for claim in ("hardware", "bench", "compliance", "commercial"):
            self.assertIn(claim, ceiling)


if __name__ == "__main__":
    unittest.main()

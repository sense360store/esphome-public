"""PRODUCT-TAXONOMY-AUDIT-001 taxonomy / terminology safeguards.

Enforces the legacy-terminology policy declared in
config/legacy-term-allowlist.json against current authoritative and
customer-facing files, and pins the binding compatibility model
(AirIQ/VentIQ mutual exclusion, RoomIQ independence, no generic Fan
token) against the machine-readable authorities:

- config/hardware-catalog.json      (board / SKU identity)
- config/product-catalog.json       (lifecycle status)
- config/webflash-builds.json       (release/build matrix)
- config/webflash-compatibility.json (config-string contract snapshot)

Deliberately narrow: only the files listed in the allowlist's
"scanned_files" are scanned for forbidden terms, so historical evidence
(docs/hardware/, docs/decisions/, release notes, CHANGELOG), compatibility
aliases (packages/expansions/, packages/hardware/), and test fixtures are
never falsely rejected. Legacy terms remain permitted on lines that carry
an explicit legacy/alias/drift marker.

Stdlib unittest only; runnable directly or under plain pytest.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = REPO_ROOT / "config" / "legacy-term-allowlist.json"
HARDWARE_CATALOG_PATH = REPO_ROOT / "config" / "hardware-catalog.json"
PRODUCT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
WEBFLASH_COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
TAXONOMY_DOC_PATH = REPO_ROOT / "docs" / "product-taxonomy.md"
BUNDLES_DIR = REPO_ROOT / "products" / "bundles"

FAN_TOKENS = {"FanRelay", "FanPWM", "FanDAC", "FanTRIAC"}
AIR_QUALITY_TOKENS = {"AirIQ", "VentIQ"}

# Sensors that config/hardware-catalog.json declares as connector-supported
# external attachments (not board-populated). Current docs may mention them
# only in lines that make the attachment relationship explicit.
CONNECTOR_ONLY_PARTS = ("SPS30", "SFA40", "MLX90614")
ATTACHMENT_CONTEXT = re.compile(
    r"connector|attach|external|optional|plug|drift|legacy|not fitted|not populated",
    re.IGNORECASE,
)

# Claims the current taxonomy doc must not make: every config released /
# Release-One as the universal architecture frame.
FORBIDDEN_TAXONOMY_CLAIMS = (
    "maps 1:1",
    "maps 1-to-1",
    "and a published `.bin` asset on the matching GitHub Release",
)


def _load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _config_tokens(config_string):
    return config_string.split("-")


class TestLegacyTermPolicy(unittest.TestCase):
    """Forbidden legacy terms stay out of current authoritative files."""

    @classmethod
    def setUpClass(cls):
        cls.policy = _load_json(ALLOWLIST_PATH)
        cls.markers = [m.lower() for m in cls.policy["legacy_marker_tokens"]]
        cls.terms = [
            (entry["label"], re.compile(entry["pattern"]))
            for entry in cls.policy["forbidden_terms"]
        ]
        cls.exceptions = [
            (exc["file"], re.compile(exc["pattern"]))
            for exc in cls.policy.get("exceptions", [])
        ]

    def _line_is_marked_legacy(self, line):
        lowered = line.lower()
        return any(marker in lowered for marker in self.markers)

    def _is_excepted(self, rel_path, pattern_match_line):
        for exc_file, exc_pattern in self.exceptions:
            if exc_file == rel_path and exc_pattern.search(pattern_match_line):
                return True
        return False

    def test_scanned_files_exist(self):
        for rel_path in self.policy["scanned_files"]:
            self.assertTrue(
                (REPO_ROOT / rel_path).is_file(),
                f"scanned file missing from tree: {rel_path}",
            )

    def test_no_forbidden_terms_in_current_files(self):
        violations = []
        for rel_path in self.policy["scanned_files"]:
            path = REPO_ROOT / rel_path
            if not path.is_file():
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            for lineno, line in enumerate(lines, start=1):
                for label, pattern in self.terms:
                    if not pattern.search(line):
                        continue
                    if self._line_is_marked_legacy(line):
                        continue
                    if self._is_excepted(rel_path, line):
                        continue
                    violations.append(
                        f"{rel_path}:{lineno}: [{label}] {line.strip()[:120]}"
                    )
        self.assertEqual(
            violations,
            [],
            "Forbidden legacy terminology in current authoritative files "
            "(add explicit legacy/alias/drift context or fix the text):\n"
            + "\n".join(violations),
        )

    def test_exceptions_reference_scanned_files(self):
        scanned = set(self.policy["scanned_files"])
        for exc in self.policy.get("exceptions", []):
            self.assertIn(
                exc["file"],
                scanned,
                f"exception for unscanned file is dead policy: {exc['file']}",
            )


class TestCompatibilityModel(unittest.TestCase):
    """AirIQ/VentIQ exclusion, RoomIQ independence, no generic Fan token."""

    @classmethod
    def setUpClass(cls):
        cls.compat = _load_json(WEBFLASH_COMPAT_PATH)
        cls.builds = _load_json(WEBFLASH_BUILDS_PATH)["builds"]
        cls.catalog = _load_json(PRODUCT_CATALOG_PATH)["products"]

    def test_contract_declares_air_quality_mutex(self):
        rules = self.compat["rules"]
        self.assertTrue(rules["airiq_and_ventiq_mutually_exclusive"])

    def test_contract_declares_roomiq_independence(self):
        rules = self.compat["rules"]
        self.assertTrue(rules["roomiq_can_pair_with_airiq"])
        self.assertTrue(rules["roomiq_can_pair_with_ventiq"])

    def test_contract_forbids_generic_fan_token(self):
        self.assertIn("Fan", self.compat["forbidden_tokens"])
        self.assertTrue(self.compat["rules"]["generic_fan_token_forbidden"])

    def test_no_build_combines_airiq_and_ventiq(self):
        for build in self.builds:
            tokens = set(_config_tokens(build["config_string"]))
            self.assertFalse(
                AIR_QUALITY_TOKENS.issubset(tokens),
                f"AirIQ and VentIQ are mutually exclusive: {build['config_string']}",
            )

    def test_no_build_uses_generic_fan_token(self):
        for build in self.builds:
            tokens = _config_tokens(build["config_string"])
            self.assertNotIn(
                "Fan",
                tokens,
                f"generic Fan token in build matrix: {build['config_string']}",
            )

    def test_no_build_combines_two_fan_drivers(self):
        for build in self.builds:
            tokens = set(_config_tokens(build["config_string"]))
            self.assertLessEqual(
                len(tokens & FAN_TOKENS),
                1,
                f"more than one fan driver: {build['config_string']}",
            )

    def test_roomiq_pairs_with_both_air_quality_modules(self):
        """RoomIQ is slot-independent: the matrix carries RoomIQ alongside
        AirIQ, alongside VentIQ, and (in the catalog) without either."""
        strings = [b["config_string"] for b in self.builds]
        self.assertTrue(
            any({"AirIQ", "RoomIQ"} <= set(_config_tokens(s)) for s in strings)
        )
        self.assertTrue(
            any({"VentIQ", "RoomIQ"} <= set(_config_tokens(s)) for s in strings)
        )
        self.assertTrue(
            any(
                "RoomIQ" in _config_tokens(s)
                and not (AIR_QUALITY_TOKENS & set(_config_tokens(s)))
                for s in strings
            )
        )


class TestTaxonomyDocAlignment(unittest.TestCase):
    """docs/product-taxonomy.md stays anchored to the machine-readable
    authorities instead of restating stale product detail."""

    @classmethod
    def setUpClass(cls):
        cls.doc = TAXONOMY_DOC_PATH.read_text(encoding="utf-8")
        cls.doc_lines = cls.doc.splitlines()
        cls.hardware = _load_json(HARDWARE_CATALOG_PATH)["items"]

    def test_every_catalog_sku_is_documented(self):
        for item in self.hardware:
            self.assertIn(
                item["sku"],
                self.doc,
                f"board SKU missing from docs/product-taxonomy.md: {item['sku']}",
            )

    def test_every_catalog_friendly_name_is_documented(self):
        for item in self.hardware:
            self.assertIn(
                item["friendly_name"],
                self.doc,
                "canonical friendly name missing from docs/product-taxonomy.md: "
                f"{item['friendly_name']}",
            )

    def test_doc_links_machine_readable_authorities(self):
        for authority in (
            "config/hardware-catalog.json",
            "config/product-catalog.json",
            "config/webflash-builds.json",
            "config/webflash-compatibility.json",
        ):
            self.assertIn(
                authority,
                self.doc,
                f"docs/product-taxonomy.md must link {authority}",
            )

    def test_doc_has_lifecycle_section(self):
        self.assertRegex(
            self.doc,
            r"(?m)^##.*[Ll]ifecycle",
            "docs/product-taxonomy.md needs a lifecycle/release-state section "
            "distinguishing capability from release status",
        )

    def test_doc_does_not_claim_every_config_is_released(self):
        for phrase in FORBIDDEN_TAXONOMY_CLAIMS:
            self.assertNotIn(
                phrase,
                self.doc,
                "docs/product-taxonomy.md must not claim every config string "
                f"has a published artifact (found: {phrase!r})",
            )

    def test_release_one_is_not_a_heading(self):
        """Release-One names the initial release programme; it must not be
        the doc's structural frame (headings) for the current taxonomy."""
        for line in self.doc_lines:
            if line.startswith("#"):
                self.assertNotIn(
                    "Release-One",
                    line,
                    f"Release-One used as taxonomy heading: {line.strip()}",
                )

    def test_connector_parts_carry_attachment_context(self):
        violations = []
        for lineno, line in enumerate(self.doc_lines, start=1):
            for part in CONNECTOR_ONLY_PARTS:
                if part in line and not ATTACHMENT_CONTEXT.search(line):
                    violations.append(f"line {lineno}: {line.strip()[:120]}")
        self.assertEqual(
            violations,
            [],
            "Connector-supported parts (SPS30/SFA40/MLX90614) must not read "
            "as board-fitted hardware in docs/product-taxonomy.md:\n"
            + "\n".join(violations),
        )


class TestBundleNamesMatchCatalog(unittest.TestCase):
    """products/bundles/ filenames follow the config-string grammar and
    round-trip against the product catalog."""

    @classmethod
    def setUpClass(cls):
        catalog = _load_json(PRODUCT_CATALOG_PATH)["products"]
        cls.catalog_strings = {
            entry["config_string"]
            for entry in catalog
            if entry.get("config_string")
        }
        cls.build_strings = {
            build["config_string"]
            for build in _load_json(WEBFLASH_BUILDS_PATH)["builds"]
        }

    def test_every_bundle_matches_a_catalog_config_string(self):
        lowered = {s.lower(): s for s in self.catalog_strings}
        for bundle in sorted(BUNDLES_DIR.glob("*.yaml")):
            self.assertIn(
                bundle.stem,
                lowered,
                f"bundle file does not match any catalog config string: "
                f"products/bundles/{bundle.name}",
            )

    def test_every_build_matrix_row_has_a_bundle(self):
        bundle_stems = {b.stem for b in BUNDLES_DIR.glob("*.yaml")}
        for config_string in sorted(self.build_strings):
            self.assertIn(
                config_string.lower(),
                bundle_stems,
                f"build matrix config string has no bundle: {config_string}",
            )


if __name__ == "__main__":
    unittest.main()

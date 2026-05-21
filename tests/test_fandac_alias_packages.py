#!/usr/bin/env python3
"""Tests for the FanDAC canonical alias package
(PACKAGE-NAMING-ALIASES-FANDAC-001).

This is the fourth Phase 2 slice after
PACKAGE-NAMING-ALIASES-VENTIQ-001 (PR #552),
PACKAGE-NAMING-ALIASES-ROOMIQ-001 (PR #553), and
PACKAGE-NAMING-ALIASES-AIRIQ-001 (PR #555), and follows
PACKAGE-NAMING-AUDIT-001 (PR #550). The naming-audit Phase 2
contract (``docs/package-naming-audit.md`` §"Phase 2 — Add
canonical aliases / wrapper packages") says each canonical alias
must be a thin wrapper that ``!include``s exactly the intended
legacy file and adds nothing else, must not rename, move, delete,
or edit the legacy file, and (per Rule 8) must add no new
substitutions, globals, or YAML blocks.

What this file checks for the FanDAC alias / legacy pair:

  * the alias file exists,
  * the alias file ``!include``s exactly the intended legacy file
    (one ``!include`` line, no other ``!include`` lines, the legacy
    target matches ``fan_gp8403.yaml``),
  * the alias filename starts with the canonical ``fan_dac`` token
    (case-insensitive match) — the lowercase ``snake_case`` rendering
    of the productized ``FanDAC`` module token from
    ``config/webflash-compatibility.json``'s ``canonical_modules``,
  * the legacy file still exists (Phase 2 must not delete or move
    legacy files),
  * the alias file is parseable YAML,
  * the alias inventory has no duplicate alias_path / legacy_path
    entries,
  * the alias is a pure wrapper and does **not** add any
    substitutions, globals, sensors, outputs, components, or
    fan-control behaviour beyond the single ``packages:`` ``!include``
    of the legacy file (Rule 8 compatibility-shim policy).

Note on the ``Fan`` forbidden token:

  The token ``Fan`` (uppercase, standalone) appears in
  ``config/webflash-compatibility.json``'s ``forbidden_tokens`` array
  as a generic / customer-facing WebFlash label that must not appear
  in WebFlash artifact filenames. The FanDAC alias filename
  ``fan_dac.yaml`` is the lowercase ``snake_case`` rendering of the
  productized canonical module token ``FanDAC`` (which is listed in
  ``canonical_modules``), not the forbidden generic ``Fan`` token.
  This file is an internal ``packages/**`` implementation alias, not
  a WebFlash artifact name; customer-facing labels remain
  outcome-first (e.g. "0–10V fan control") and are surfaced
  elsewhere. The forbidden-token assertion used by the VentIQ /
  RoomIQ / AirIQ alias tests is therefore intentionally **not**
  applied here — the audit's Phase-2 inventory explicitly proposes
  ``fan_dac.yaml`` as the canonical alias for ``fan_gp8403.yaml``
  (``docs/package-naming-audit.md`` §"Phase 2 — Add canonical
  aliases / wrapper packages" inventory table).

These are deliberately file-content / structural checks — they do
not require an ESPHome compile.

Run with::

    python3 tests/test_fandac_alias_packages.py

or::

    python3 -m unittest tests.test_fandac_alias_packages -v
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

PACKAGES_EXPANSIONS = REPO_ROOT / "packages" / "expansions"


# Mapping of canonical FanDAC alias filename -> legacy filename it
# wraps. Both filenames are bare basenames; the alias and legacy file
# always live in the same packages/** subdirectory so the !include
# target is a bare filename, not a relative path.
FANDAC_ALIASES = [
    {
        "alias_path": PACKAGES_EXPANSIONS / "fan_dac.yaml",
        "legacy_path": PACKAGES_EXPANSIONS / "fan_gp8403.yaml",
        "legacy_basename": "fan_gp8403.yaml",
    },
]


# Match any line in the form `<key>: !include <target>` so we can pin
# both the count of !include directives and the target filename.
INCLUDE_LINE_RE = re.compile(
    r"^\s*[A-Za-z0-9_\-]+\s*:\s*!include\s+(\S+)\s*$",
    re.MULTILINE,
)


# Top-level YAML keys that would indicate the alias file is not a pure
# wrapper. Per naming-audit Rule 8 (docs/package-naming-audit.md §"Rule
# 8 — Compatibility shims live in the repo, never in customer YAML"),
# the canonical-name file must `!include` the legacy file and add no
# new substitutions or globals. The legacy `fan_gp8403.yaml` declares
# substitutions, a `gp8403:` component, `output:`, `fan:`, `sensor:`,
# `globals:`, and `script:` blocks; the alias must not redeclare any of
# them, must not add any new ones, and must not add any other
# fan-control behaviour. The single permitted top-level key is
# `packages:` (which carries the !include).
FORBIDDEN_TOP_LEVEL_KEYS_FOR_PURE_WRAPPER = (
    "substitutions",
    "globals",
    "sensor",
    "binary_sensor",
    "output",
    "fan",
    "switch",
    "script",
    "gp8403",
    "i2c",
    "uart",
    "spi",
    "esphome",
    "esp32",
    "esp8266",
    "wifi",
    "api",
    "ota",
    "logger",
    "mqtt",
    "interval",
    "button",
    "number",
    "select",
    "text_sensor",
    "climate",
    "cover",
    "light",
    "lock",
    "media_player",
    "valve",
)


def _yaml_loader_with_esphome_tags() -> type:
    """Return a SafeLoader subclass that tolerates ESPHome custom tags.

    ``yaml.safe_load`` chokes on ``!include`` / ``!secret`` / ``!lambda``
    etc. ESPHome's documented YAML tag set. For structural checks we
    only need to parse the document, so we install permissive
    constructors that return the raw scalar value.
    """

    class _Loader(yaml.SafeLoader):
        pass

    def _constructor(loader, node):
        if isinstance(node, yaml.ScalarNode):
            return loader.construct_scalar(node)
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        if isinstance(node, yaml.MappingNode):
            return loader.construct_mapping(node)
        return None

    for tag in ("!include", "!secret", "!extend", "!lambda", "!remove"):
        _Loader.add_constructor(tag, _constructor)
    _Loader.add_multi_constructor("!include_dir_", _constructor)
    return _Loader


_YAML_LOADER = _yaml_loader_with_esphome_tags()


class FanDACAliasExistenceTests(unittest.TestCase):
    """Each FanDAC alias file must exist on disk."""

    def test_alias_files_exist(self) -> None:
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.is_file(),
                    f"missing FanDAC alias file: {alias_path}",
                )


class FanDACAliasYAMLParseTests(unittest.TestCase):
    """Each FanDAC alias file must be parseable YAML."""

    def test_alias_parses(self) -> None:
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                try:
                    yaml.load(alias_path.read_text(), Loader=_YAML_LOADER)
                except yaml.YAMLError as exc:
                    self.fail(
                        f"FanDAC alias {alias_path} has invalid YAML: {exc}"
                    )


class FanDACAliasIncludeTargetTests(unittest.TestCase):
    """Each alias must !include exactly the intended legacy file."""

    def test_alias_includes_exactly_one_legacy_target(self) -> None:
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            legacy_basename: str = entry["legacy_basename"]
            with self.subTest(alias=alias_path.name):
                text = alias_path.read_text()
                matches = INCLUDE_LINE_RE.findall(text)
                self.assertEqual(
                    len(matches),
                    1,
                    f"FanDAC alias {alias_path} must contain exactly one "
                    f"'<key>: !include <target>' line. Found {len(matches)}: "
                    f"{matches!r}. Phase 2 aliases are pure wrappers — they "
                    "must include the legacy file and nothing else.",
                )
                target = matches[0]
                self.assertEqual(
                    target,
                    legacy_basename,
                    f"FanDAC alias {alias_path} must !include the bare "
                    f"basename {legacy_basename!r} of the legacy "
                    "implementation file (the alias and legacy file live "
                    "in the same packages/** subdirectory). Found "
                    f"{target!r}.",
                )

    def test_alias_includes_fan_gp8403(self) -> None:
        """Belt-and-braces: pin the specific legacy target."""

        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                text = alias_path.read_text()
                matches = INCLUDE_LINE_RE.findall(text)
                self.assertEqual(
                    matches,
                    ["fan_gp8403.yaml"],
                    f"FanDAC alias {alias_path} must !include exactly "
                    "'fan_gp8403.yaml' as the legacy implementation "
                    "source-of-truth. Found include targets: "
                    f"{matches!r}.",
                )


class FanDACAliasStartsWithFanDACTests(unittest.TestCase):
    """Each canonical alias filename must start with the productized ``fan_dac`` token.

    The lowercase ``snake_case`` ``fan_dac`` is the rendering of the
    productized canonical module token ``FanDAC`` from
    ``config/webflash-compatibility.json``'s ``canonical_modules`` array.
    The alias filename is the only signal that distinguishes the
    canonical wrapper from the legacy vendor-chip filename
    (``fan_gp8403.yaml``).
    """

    def test_alias_filename_starts_with_fan_dac(self) -> None:
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.stem.lower().startswith("fan_dac"),
                    f"FanDAC alias filename {alias_path.name!r} must start "
                    "with the canonical productized 'fan_dac' token "
                    "(the lowercase snake_case rendering of the "
                    "canonical 'FanDAC' module in "
                    "config/webflash-compatibility.json's "
                    "canonical_modules array). The alias filename is the "
                    "only signal that distinguishes the canonical "
                    "wrapper from the legacy vendor-chip filename "
                    "fan_gp8403.yaml.",
                )


class FanDACAliasLegacyFilePreservedTests(unittest.TestCase):
    """Phase 2 must not delete or move the legacy implementation files."""

    def test_legacy_file_still_exists(self) -> None:
        for entry in FANDAC_ALIASES:
            legacy_path: Path = entry["legacy_path"]
            with self.subTest(legacy=legacy_path.name):
                self.assertTrue(
                    legacy_path.is_file(),
                    f"legacy implementation file {legacy_path} is missing. "
                    "Phase 2 aliases are wrappers — the legacy file must "
                    "remain in place as the source of truth.",
                )


class FanDACAliasPureWrapperTests(unittest.TestCase):
    """The alias must be a pure include wrapper — no extra YAML blocks.

    Per naming-audit Rule 8 (docs/package-naming-audit.md §"Rule 8 —
    Compatibility shims live in the repo, never in customer YAML"), the
    canonical-name file must `!include` the legacy file and add no new
    substitutions or globals. This test pins that contract:

      * the top-level YAML document is a mapping,
      * the only top-level key is ``packages``,
      * no substitution / global / sensor / output / component / fan
        / script / interval block appears anywhere in the alias file.

    The legacy `fan_gp8403.yaml` declares substitutions, a `gp8403`
    component, `output:`, `fan:`, `sensor:`, `globals:`, and `script:`
    blocks; the alias must not redeclare any of them, must not add any
    new ones, and must not add any fan-control behaviour. The single
    permitted top-level key is `packages:` (carrying the !include).
    """

    def test_alias_only_has_packages_top_level_key(self) -> None:
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                doc = yaml.load(alias_path.read_text(), Loader=_YAML_LOADER)
                self.assertIsInstance(
                    doc,
                    dict,
                    f"FanDAC alias {alias_path} must parse to a top-level "
                    "YAML mapping. A pure-wrapper alias is a single "
                    "`packages:` block.",
                )
                top_level_keys = set(doc.keys())
                self.assertEqual(
                    top_level_keys,
                    {"packages"},
                    f"FanDAC alias {alias_path} must contain exactly one "
                    "top-level key — `packages:` — carrying the single "
                    "!include of the legacy file. Found top-level keys: "
                    f"{sorted(top_level_keys)!r}. Per naming-audit Rule "
                    "8 (docs/package-naming-audit.md §'Rule 8 — "
                    "Compatibility shims live in the repo, never in "
                    "customer YAML'), the canonical-name file must "
                    "`!include` the legacy file and add no new "
                    "substitutions or globals.",
                )

    def test_alias_does_not_redeclare_legacy_yaml_blocks(self) -> None:
        """Belt-and-braces: scan the raw text for forbidden top-level keys.

        Even if `yaml.load` collapses the document differently under
        future PyYAML versions, this regex-based check pins that no
        top-level block from the forbidden list appears at column 0 in
        the alias file (commented-out occurrences inside the comment
        header are explicitly tolerated).
        """

        top_level_key_re = re.compile(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s*:",
            re.MULTILINE,
        )
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                # Strip comments before matching so that prose mentions of
                # the forbidden keys inside the comment header (which
                # explain why the alias is a pure wrapper) do not trigger
                # a false positive.
                stripped = "\n".join(
                    line for line in alias_path.read_text().splitlines()
                    if not line.lstrip().startswith("#")
                )
                top_level_keys = set(top_level_key_re.findall(stripped))
                for key in FORBIDDEN_TOP_LEVEL_KEYS_FOR_PURE_WRAPPER:
                    self.assertNotIn(
                        key,
                        top_level_keys,
                        f"FanDAC alias {alias_path} declares a forbidden "
                        f"top-level block {key!r}. Per naming-audit "
                        "Rule 8, the alias must be a pure include "
                        "wrapper around the legacy file and must not "
                        "redeclare any substitution / global / sensor "
                        "/ output / component / fan / script block. The "
                        "legacy `fan_gp8403.yaml` is the source of truth "
                        "for all fan-control behaviour.",
                    )

    def test_alias_does_not_contain_fan_control_behavior(self) -> None:
        """Belt-and-braces: pin that the alias contains no `gp8403:` /
        `fan:` / `output:` declarations or any embedded lambda /
        automation that would change runtime behaviour.

        This catches a hypothetical regression where someone adds an
        in-place fan-control block to the alias file instead of relying
        on the legacy `!include`. The legacy file already declares the
        `gp8403:` DAC component, two DAC outputs, two `fan` speed
        controllers, monitoring sensors, globals, and emergency-stop
        scripts; the alias must add none of these.
        """

        # Lowercased line-prefix tokens that, if present at the start of
        # any non-comment line, would indicate the alias is no longer a
        # pure wrapper. Each token below maps to a fan-control / driver
        # block in the legacy file.
        forbidden_line_prefixes = (
            "gp8403:",
            "fan:",
            "output:",
            "sensor:",
            "globals:",
            "script:",
            "substitutions:",
            "binary_sensor:",
            "switch:",
        )
        for entry in FANDAC_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                for raw_line in alias_path.read_text().splitlines():
                    if raw_line.lstrip().startswith("#"):
                        continue
                    line = raw_line.rstrip()
                    if not line:
                        continue
                    for prefix in forbidden_line_prefixes:
                        self.assertFalse(
                            line.startswith(prefix),
                            f"FanDAC alias {alias_path} contains a "
                            f"top-level {prefix!r} declaration. Per "
                            "naming-audit Rule 8, the alias must stay "
                            "a pure include wrapper around "
                            "`fan_gp8403.yaml`. Move the implementation "
                            "into the legacy file (which is the source "
                            "of truth) and leave the alias as the "
                            "single `packages:` `!include` line.",
                        )


class FanDACAliasInventoryCoverageTests(unittest.TestCase):
    """Belt-and-braces: pin the one-alias inventory shape."""

    def test_inventory_has_one_entry(self) -> None:
        self.assertEqual(
            len(FANDAC_ALIASES),
            1,
            "Expected exactly one FanDAC Phase-2 alias entry "
            "(`packages/expansions/fan_dac.yaml` wrapping "
            "`packages/expansions/fan_gp8403.yaml`). If a new alias is "
            "added (e.g. a future `fan_dac_profile.yaml` feature-side "
            "alias), extend the inventory and the assertion together so "
            "the test count cannot silently drift.",
        )

    def test_inventory_alias_paths_are_unique(self) -> None:
        alias_paths = [entry["alias_path"] for entry in FANDAC_ALIASES]
        self.assertEqual(
            len(alias_paths),
            len(set(alias_paths)),
            "FanDAC alias inventory contains duplicate alias_path entries.",
        )

    def test_inventory_legacy_paths_are_unique(self) -> None:
        legacy_paths = [entry["legacy_path"] for entry in FANDAC_ALIASES]
        self.assertEqual(
            len(legacy_paths),
            len(set(legacy_paths)),
            "FanDAC alias inventory contains duplicate legacy_path entries.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

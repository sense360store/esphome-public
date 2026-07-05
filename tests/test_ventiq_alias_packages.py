#!/usr/bin/env python3
"""Tests for the VentIQ canonical alias packages
(PACKAGE-NAMING-ALIASES-VENTIQ-001).

This is the Phase 2 follow-up to PACKAGE-NAMING-AUDIT-001 (PR #550).
The naming-audit Phase 2 contract (``docs/package-naming-audit.md``
§"Phase 2 — Add canonical aliases / wrapper packages"; archived under
DOCS-DISPOSITION-001, see ``docs/archive-index.md``; every citation of
it in this file refers to that archived contract) says each
canonical alias must be a thin wrapper that ``!include``s exactly the
intended legacy file and adds nothing else, must not use any
deprecated / forbidden WebFlash token in its filename, and must not
rename, move, delete, or edit the legacy file.

What this file checks for each alias / legacy pair:

  * the alias file exists,
  * the alias file ``!include``s exactly the intended legacy file
    (one ``!include`` line, no other ``!include`` lines, the legacy
    target matches),
  * the alias filename contains no forbidden customer-facing token
    listed in ``config/webflash-compatibility.json``'s
    ``forbidden_tokens`` (``Bathroom``, ``Comfort``, ``Presence``,
    generic ``Fan``, ``FanAnalog``),
  * the alias filename starts with the canonical ``VentIQ`` token
    (case-insensitive match against ``ventiq``),
  * the legacy file still exists (Phase 2 must not delete or move
    legacy files),
  * the alias file is parseable YAML.

These are deliberately file-content / structural checks — they do
not require an ESPHome compile.

Run with::

    python3 tests/test_ventiq_alias_packages.py

or::

    python3 -m unittest tests.test_ventiq_alias_packages -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

PACKAGES_EXPANSIONS = REPO_ROOT / "packages" / "expansions"
PACKAGES_FEATURES = REPO_ROOT / "packages" / "features"

WEBFLASH_COMPATIBILITY = REPO_ROOT / "config" / "webflash-compatibility.json"


# Mapping of canonical VentIQ alias filename -> legacy filename it
# wraps. Both filenames are bare basenames; the alias and legacy file
# always live in the same packages/** subdirectory so the !include
# target is a bare filename, not a relative path.
VENTIQ_ALIASES = [
    {
        "alias_path": PACKAGES_EXPANSIONS / "ventiq.yaml",
        "legacy_path": PACKAGES_EXPANSIONS / "airiq_bathroom_base.yaml",
        "legacy_basename": "airiq_bathroom_base.yaml",
    },
    {
        "alias_path": PACKAGES_FEATURES / "ventiq_profile.yaml",
        "legacy_path": PACKAGES_FEATURES / "bathroom_profile.yaml",
        "legacy_basename": "bathroom_profile.yaml",
    },
]


# Match any line in the form `<key>: !include <target>` so we can pin
# both the count of !include directives and the target filename.
INCLUDE_LINE_RE = re.compile(
    r"^\s*[A-Za-z0-9_\-]+\s*:\s*!include\s+(\S+)\s*$",
    re.MULTILINE,
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


def _load_forbidden_tokens() -> list[str]:
    """Read the forbidden_tokens list from webflash-compatibility.json."""

    doc = json.loads(WEBFLASH_COMPATIBILITY.read_text())
    tokens = doc.get("forbidden_tokens", [])
    if not isinstance(tokens, list):
        raise AssertionError(
            "webflash-compatibility.json forbidden_tokens must be a list"
        )
    return tokens


class VentIQAliasExistenceTests(unittest.TestCase):
    """Each VentIQ alias file must exist on disk."""

    def test_alias_files_exist(self) -> None:
        for entry in VENTIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.is_file(),
                    f"missing VentIQ alias file: {alias_path}",
                )


class VentIQAliasYAMLParseTests(unittest.TestCase):
    """Each VentIQ alias file must be parseable YAML."""

    def test_alias_parses(self) -> None:
        for entry in VENTIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                try:
                    yaml.load(alias_path.read_text(), Loader=_YAML_LOADER)
                except yaml.YAMLError as exc:
                    self.fail(
                        f"VentIQ alias {alias_path} has invalid YAML: {exc}"
                    )


class VentIQAliasIncludeTargetTests(unittest.TestCase):
    """Each alias must !include exactly the intended legacy file."""

    def test_alias_includes_exactly_one_legacy_target(self) -> None:
        for entry in VENTIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            legacy_basename: str = entry["legacy_basename"]
            with self.subTest(alias=alias_path.name):
                text = alias_path.read_text()
                matches = INCLUDE_LINE_RE.findall(text)
                self.assertEqual(
                    len(matches),
                    1,
                    f"VentIQ alias {alias_path} must contain exactly one "
                    f"'<key>: !include <target>' line. Found {len(matches)}: "
                    f"{matches!r}. Phase 2 aliases are pure wrappers — they "
                    "must include the legacy file and nothing else.",
                )
                target = matches[0]
                self.assertEqual(
                    target,
                    legacy_basename,
                    f"VentIQ alias {alias_path} must !include the bare "
                    f"basename {legacy_basename!r} of the legacy "
                    "implementation file (the alias and legacy file live "
                    "in the same packages/** subdirectory). Found "
                    f"{target!r}.",
                )


class VentIQAliasNoForbiddenTokenTests(unittest.TestCase):
    """Alias filenames must not contain any forbidden customer-facing token.

    The forbidden token list is the ``forbidden_tokens`` array in
    ``config/webflash-compatibility.json``. Matching is
    case-insensitive against the alias basename so e.g. an alias
    ``ventiq_bathroom_profile.yaml`` would fail because it carries the
    forbidden ``Bathroom`` token. The naming-audit Rule 7 requires that
    deprecated WebFlash tokens never appear in newly added package
    filenames.
    """

    def setUp(self) -> None:
        self.forbidden_tokens = _load_forbidden_tokens()

    def test_alias_filename_has_no_forbidden_token(self) -> None:
        for entry in VENTIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                name_lower = alias_path.name.lower()
                for token in self.forbidden_tokens:
                    self.assertNotIn(
                        token.lower(),
                        name_lower,
                        f"VentIQ alias filename {alias_path.name!r} carries "
                        f"the forbidden customer-facing token {token!r} "
                        "from config/webflash-compatibility.json's "
                        "forbidden_tokens list. Per naming-audit Rule 7 "
                        "(docs/package-naming-audit.md §'Rule 7 — "
                        "Deprecated WebFlash tokens must not appear in "
                        "new filenames'), new package filenames must not "
                        "use any deprecated WebFlash token.",
                    )


class VentIQAliasStartsWithVentIQTests(unittest.TestCase):
    """Each canonical alias filename must start with the productized ``ventiq`` token."""

    def test_alias_filename_starts_with_ventiq(self) -> None:
        for entry in VENTIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.stem.lower().startswith("ventiq"),
                    f"VentIQ alias filename {alias_path.name!r} must start "
                    "with the canonical productized 'ventiq' token. The "
                    "alias filename is the only signal that distinguishes "
                    "the canonical wrapper from the legacy implementation "
                    "file.",
                )


class VentIQAliasLegacyFilePreservedTests(unittest.TestCase):
    """Phase 2 must not delete or move the legacy implementation files."""

    def test_legacy_file_still_exists(self) -> None:
        for entry in VENTIQ_ALIASES:
            legacy_path: Path = entry["legacy_path"]
            with self.subTest(legacy=legacy_path.name):
                self.assertTrue(
                    legacy_path.is_file(),
                    f"legacy implementation file {legacy_path} is missing. "
                    "Phase 2 aliases are wrappers — the legacy file must "
                    "remain in place as the source of truth.",
                )


class VentIQAliasInventoryCoverageTests(unittest.TestCase):
    """Belt-and-braces: pin the two-alias inventory shape."""

    def test_inventory_has_two_entries(self) -> None:
        self.assertEqual(
            len(VENTIQ_ALIASES),
            2,
            "Expected exactly two VentIQ canonical alias entries "
            "(ventiq.yaml, ventiq_profile.yaml). The abandoned pro/extended "
            "tier aliases (ventiq_extended.yaml, ventiq_extended_profile.yaml) "
            "and their legacy targets were removed. If a new alias is added, "
            "extend the inventory and the assertion together so the "
            "test count cannot silently drift.",
        )

    def test_inventory_alias_paths_are_unique(self) -> None:
        alias_paths = [entry["alias_path"] for entry in VENTIQ_ALIASES]
        self.assertEqual(
            len(alias_paths),
            len(set(alias_paths)),
            "VentIQ alias inventory contains duplicate alias_path entries.",
        )

    def test_inventory_legacy_paths_are_unique(self) -> None:
        legacy_paths = [entry["legacy_path"] for entry in VENTIQ_ALIASES]
        self.assertEqual(
            len(legacy_paths),
            len(set(legacy_paths)),
            "VentIQ alias inventory contains duplicate legacy_path entries.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

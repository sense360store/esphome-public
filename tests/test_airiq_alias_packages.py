#!/usr/bin/env python3
"""Tests for the AirIQ canonical alias packages
(PACKAGE-NAMING-ALIASES-AIRIQ-001).

This is the third Phase 2 slice after
PACKAGE-NAMING-ALIASES-VENTIQ-001 (PR #552) and
PACKAGE-NAMING-ALIASES-ROOMIQ-001 (PR #553), and follows
PACKAGE-NAMING-AUDIT-001 (PR #550). The naming-audit Phase 2
contract (``docs/package-naming-audit.md`` §"Phase 2 — Add
canonical aliases / wrapper packages") says each canonical alias
must be a thin wrapper that ``!include``s exactly the intended
legacy file and adds nothing else, must not use any deprecated /
forbidden WebFlash token in its filename, and must not rename,
move, delete, or edit the legacy file.

What this file checks for each alias / legacy pair:

  * the alias file exists,
  * the alias file ``!include``s exactly the intended legacy file
    (one ``!include`` line, no other ``!include`` lines, the legacy
    target matches),
  * the alias filename contains no forbidden customer-facing token
    listed in ``config/webflash-compatibility.json``'s
    ``forbidden_tokens`` (``Bathroom``, ``Comfort``, ``Presence``,
    generic ``Fan``, ``FanAnalog``),
  * the alias filename starts with the canonical ``AirIQ`` token
    (case-insensitive match against ``airiq``),
  * the legacy file still exists (Phase 2 must not delete or move
    legacy files),
  * the alias file is parseable YAML,
  * any alias whose legacy target carries fan-control /
    auto-ventilation behaviour (i.e. drives a fan output / fan
    switch) carries a behaviour-revealing term such as
    ``auto_ventilation`` in its filename, per naming-audit Rule 6
    (``docs/package-naming-audit.md`` §"Rule 6 — Avoid package
    names that hide control behavior").

These are deliberately file-content / structural checks — they do
not require an ESPHome compile.

Run with::

    python3 tests/test_airiq_alias_packages.py

or::

    python3 -m unittest tests.test_airiq_alias_packages -v
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


# Mapping of canonical AirIQ alias filename -> legacy filename it
# wraps. Both filenames are bare basenames; the alias and legacy file
# always live in the same packages/** subdirectory so the !include
# target is a bare filename, not a relative path.
#
# The ``has_fan_control_behavior`` flag pins which legacy targets
# actually drive a fan output / fan switch under the hood. The
# audit (docs/package-naming-audit.md §"AirIQ packages") flags
# ``airiq_advanced_profile.yaml`` as ``behavior-hidden-by-name``
# because it declares a `gpio` output on `GPIO15`, a `fan_switch`
# template switch, and an `auto_fan_control` script that toggles
# the switch on changes to `air_quality_state`. Per naming-audit
# Rule 6, the canonical alias filename for such legacy files must
# carry a behaviour-revealing term so the hidden fan-control
# behaviour is visible at a glance from the include path.
AIRIQ_ALIASES = [
    {
        "alias_path": PACKAGES_FEATURES / "airiq_profile.yaml",
        "legacy_path": PACKAGES_FEATURES / "airiq_basic.yaml",
        "legacy_basename": "airiq_basic.yaml",
        "has_fan_control_behavior": False,
    },
    {
        "alias_path": PACKAGES_FEATURES / "airiq_extended_profile.yaml",
        "legacy_path": PACKAGES_FEATURES / "airiq_advanced.yaml",
        "legacy_basename": "airiq_advanced.yaml",
        "has_fan_control_behavior": False,
    },
    {
        "alias_path": PACKAGES_FEATURES / "airiq_mqtt_profile.yaml",
        "legacy_path": PACKAGES_FEATURES / "airiq_basic_profile.yaml",
        "legacy_basename": "airiq_basic_profile.yaml",
        "has_fan_control_behavior": False,
    },
    {
        "alias_path": PACKAGES_FEATURES / "airiq_auto_ventilation_profile.yaml",
        "legacy_path": PACKAGES_FEATURES / "airiq_advanced_profile.yaml",
        "legacy_basename": "airiq_advanced_profile.yaml",
        "has_fan_control_behavior": True,
    },
]


# Terms that count as behaviour-revealing for fan-control /
# auto-ventilation behaviour. The token ``fan`` is on the WebFlash
# forbidden-tokens list, so the canonical alias filename must not
# contain ``fan`` — it must instead use one of the neutral
# behaviour-revealing terms below.
BEHAVIOR_REVEALING_TERMS_FOR_FAN_CONTROL = (
    "auto_ventilation",
    "auto_exchange",
    "ventilation",
    "air_exchange",
)


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


class AirIQAliasExistenceTests(unittest.TestCase):
    """Each AirIQ alias file must exist on disk."""

    def test_alias_files_exist(self) -> None:
        for entry in AIRIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.is_file(),
                    f"missing AirIQ alias file: {alias_path}",
                )


class AirIQAliasYAMLParseTests(unittest.TestCase):
    """Each AirIQ alias file must be parseable YAML."""

    def test_alias_parses(self) -> None:
        for entry in AIRIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                try:
                    yaml.load(alias_path.read_text(), Loader=_YAML_LOADER)
                except yaml.YAMLError as exc:
                    self.fail(
                        f"AirIQ alias {alias_path} has invalid YAML: {exc}"
                    )


class AirIQAliasIncludeTargetTests(unittest.TestCase):
    """Each alias must !include exactly the intended legacy file."""

    def test_alias_includes_exactly_one_legacy_target(self) -> None:
        for entry in AIRIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            legacy_basename: str = entry["legacy_basename"]
            with self.subTest(alias=alias_path.name):
                text = alias_path.read_text()
                matches = INCLUDE_LINE_RE.findall(text)
                self.assertEqual(
                    len(matches),
                    1,
                    f"AirIQ alias {alias_path} must contain exactly one "
                    f"'<key>: !include <target>' line. Found {len(matches)}: "
                    f"{matches!r}. Phase 2 aliases are pure wrappers — they "
                    "must include the legacy file and nothing else.",
                )
                target = matches[0]
                self.assertEqual(
                    target,
                    legacy_basename,
                    f"AirIQ alias {alias_path} must !include the bare "
                    f"basename {legacy_basename!r} of the legacy "
                    "implementation file (the alias and legacy file live "
                    "in the same packages/** subdirectory). Found "
                    f"{target!r}.",
                )


class AirIQAliasNoForbiddenTokenTests(unittest.TestCase):
    """Alias filenames must not contain any forbidden customer-facing token.

    The forbidden token list is the ``forbidden_tokens`` array in
    ``config/webflash-compatibility.json``. Matching is
    case-insensitive against the alias basename so e.g. an alias
    ``airiq_fan_profile.yaml`` would fail because it carries the
    forbidden generic ``Fan`` token. The naming-audit Rule 7 requires
    that deprecated WebFlash tokens never appear in newly added
    package filenames.
    """

    def setUp(self) -> None:
        self.forbidden_tokens = _load_forbidden_tokens()

    def test_alias_filename_has_no_forbidden_token(self) -> None:
        for entry in AIRIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                name_lower = alias_path.name.lower()
                for token in self.forbidden_tokens:
                    self.assertNotIn(
                        token.lower(),
                        name_lower,
                        f"AirIQ alias filename {alias_path.name!r} carries "
                        f"the forbidden customer-facing token {token!r} "
                        "from config/webflash-compatibility.json's "
                        "forbidden_tokens list. Per naming-audit Rule 7 "
                        "(docs/package-naming-audit.md §'Rule 7 — "
                        "Deprecated WebFlash tokens must not appear in "
                        "new filenames'), new package filenames must not "
                        "use any deprecated WebFlash token.",
                    )


class AirIQAliasStartsWithAirIQTests(unittest.TestCase):
    """Each canonical alias filename must start with the productized ``airiq`` token."""

    def test_alias_filename_starts_with_airiq(self) -> None:
        for entry in AIRIQ_ALIASES:
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                self.assertTrue(
                    alias_path.stem.lower().startswith("airiq"),
                    f"AirIQ alias filename {alias_path.name!r} must start "
                    "with the canonical productized 'airiq' token. The "
                    "alias filename is the only signal that distinguishes "
                    "the canonical wrapper from the legacy implementation "
                    "file.",
                )


class AirIQAliasLegacyFilePreservedTests(unittest.TestCase):
    """Phase 2 must not delete or move the legacy implementation files."""

    def test_legacy_file_still_exists(self) -> None:
        for entry in AIRIQ_ALIASES:
            legacy_path: Path = entry["legacy_path"]
            with self.subTest(legacy=legacy_path.name):
                self.assertTrue(
                    legacy_path.is_file(),
                    f"legacy implementation file {legacy_path} is missing. "
                    "Phase 2 aliases are wrappers — the legacy file must "
                    "remain in place as the source of truth.",
                )


class AirIQAliasBehaviorRevealingNameTests(unittest.TestCase):
    """Aliases for legacy files with fan-control behaviour must reveal it.

    Per naming-audit Rule 6 (docs/package-naming-audit.md §"Rule 6 —
    Avoid package names that hide control behavior"), a package that
    performs control behaviour (GPIO output, fan switch, relay
    actuation, automation script that toggles a switch) must carry
    that behaviour in its filename. The legacy
    ``airiq_advanced_profile.yaml`` is the
    ``behavior-hidden-by-name`` case the audit flagged: an "AirIQ
    advanced" filename that actually drives a fan output on GPIO15.
    Its canonical alias filename must therefore include a
    behaviour-revealing term such as ``auto_ventilation``.
    """

    def test_fan_control_aliases_have_behavior_revealing_name(self) -> None:
        for entry in AIRIQ_ALIASES:
            if not entry["has_fan_control_behavior"]:
                continue
            alias_path: Path = entry["alias_path"]
            with self.subTest(alias=alias_path.name):
                name_lower = alias_path.name.lower()
                matched_term = None
                for term in BEHAVIOR_REVEALING_TERMS_FOR_FAN_CONTROL:
                    if term in name_lower:
                        matched_term = term
                        break
                self.assertIsNotNone(
                    matched_term,
                    f"AirIQ alias {alias_path.name!r} wraps a legacy file "
                    f"({entry['legacy_basename']!r}) that drives fan-control / "
                    "auto-ventilation behaviour (GPIO output, fan_switch, "
                    "auto_fan_control script), but the alias filename does "
                    "not contain any behaviour-revealing term. Per "
                    "naming-audit Rule 6 (docs/package-naming-audit.md "
                    "§'Rule 6 — Avoid package names that hide control "
                    "behavior'), the canonical alias must name the hidden "
                    "behaviour. Use one of: "
                    f"{BEHAVIOR_REVEALING_TERMS_FOR_FAN_CONTROL!r}.",
                )


class AirIQAliasInventoryCoverageTests(unittest.TestCase):
    """Belt-and-braces: pin the four-alias inventory shape."""

    def test_inventory_has_four_entries(self) -> None:
        self.assertEqual(
            len(AIRIQ_ALIASES),
            4,
            "Expected exactly four AirIQ Phase-2 alias entries "
            "(airiq_profile.yaml, airiq_extended_profile.yaml, "
            "airiq_mqtt_profile.yaml, "
            "airiq_auto_ventilation_profile.yaml). If a new alias is "
            "added, extend the inventory and the assertion together so "
            "the test count cannot silently drift.",
        )

    def test_inventory_alias_paths_are_unique(self) -> None:
        alias_paths = [entry["alias_path"] for entry in AIRIQ_ALIASES]
        self.assertEqual(
            len(alias_paths),
            len(set(alias_paths)),
            "AirIQ alias inventory contains duplicate alias_path entries.",
        )

    def test_inventory_legacy_paths_are_unique(self) -> None:
        legacy_paths = [entry["legacy_path"] for entry in AIRIQ_ALIASES]
        self.assertEqual(
            len(legacy_paths),
            len(set(legacy_paths)),
            "AirIQ alias inventory contains duplicate legacy_path entries.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

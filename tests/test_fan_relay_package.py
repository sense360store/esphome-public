#!/usr/bin/env python3
"""PACKAGE-RELAY-001 invariants for ``packages/expansions/fan_relay.yaml``.

These tests reconcile the FanRelay package after the two prior Core
substitution-layer slices closed at the package-evidence layer:

* ``CORE-ABSTRACT-BUS-001C`` / PR #557 freed ``GPIO3`` (the schematic
  ``Relay`` net per ``S360-100-R4`` ``IO3``) by moving the
  ``comfort_ceiling_als_int_pin`` / ``expander_int_pin`` /
  ``sx1509_interrupt_pin`` substitutions off ``GPIO3``.
* ``CORE-ABSTRACT-BUS-001A`` / PR #558 rebound ``relay_pin`` to
  ``GPIO3`` in the five non-voice Core abstract packages
  (``sense360_core.yaml``, ``sense360_core_ceiling.yaml``,
  ``sense360_core_mapping.yaml``, ``sense360_core_poe.yaml``,
  ``sense360_core_wall.yaml``).

The FanRelay package was already structurally correct against this
post-001A / 001C state:
``packages/expansions/fan_relay.yaml`` declares
``fan_relay_pin: ${relay_pin}`` and exposes its relay output through
the substitution layer. PACKAGE-RELAY-001 is therefore reconciled at
the package layer as a **test + readiness** PR — no YAML rebind, no
hardcoded GPIO, no behaviour change.

What this file checks:

  * ``packages/expansions/fan_relay.yaml`` exists and parses as YAML.
  * The package declares ``fan_relay_pin: ${relay_pin}`` as the
    default substitution (so it inherits the parent Core abstract
    package binding).
  * The package does **not** hard-code ``GPIO3`` / ``GPIO4`` /
    ``GPIO10`` (or any other ``GPIO``) on an active substitution or
    binding line — the relay output / switch must be exposed through
    the substitution layer.
  * The ``switch.platform: gpio`` block declaring
    ``id: fan_relay_switch`` binds ``pin: ${fan_relay_pin}``, so the
    switch consumes the substitution rather than a fixed pin.
  * The five non-voice Core abstract packages bind
    ``relay_pin: GPIO3`` (cross-check against the schematic-correct
    value pinned by ``tests/test_core_abstract_bus.py``).
  * The voice-variant Core packages
    (``sense360_core_voice_ceiling.yaml`` /
    ``sense360_core_voice_wall.yaml``) remain at the pre-001A
    ``relay_pin: GPIO4`` — they are deliberately out of scope for
    the 001A / PACKAGE-RELAY-001 reconciliation.
  * No WebFlash / product / release / firmware / catalog file is
    touched by PACKAGE-RELAY-001 (the YAML package layer is the only
    place where the FanRelay reconciliation is allowed).

These are deliberately file-content / structural checks — they do not
require an ESPHome compile.

Run with::

    python3 tests/test_fan_relay_package.py

or::

    python3 -m unittest tests.test_fan_relay_package -v
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

FAN_RELAY_PACKAGE = REPO_ROOT / "packages" / "expansions" / "fan_relay.yaml"

# Five non-voice Core abstract packages rebound by CORE-ABSTRACT-BUS-001A
# to the schematic-correct ``relay_pin: GPIO3`` (per ``S360-100-R4``
# ``IO3 = Relay``). Voice-variant Core packages are deliberately out of
# scope for the 001A slice and for PACKAGE-RELAY-001; they remain at
# the pre-001A ``relay_pin: GPIO4`` value.
NON_VOICE_CORE_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_mapping.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_poe.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_wall.yaml",
]

VOICE_CORE_PACKAGES = [
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_ceiling.yaml",
    REPO_ROOT / "packages" / "hardware" / "sense360_core_voice_wall.yaml",
]


# Register the same minimal set of ESPHome custom tags used by
# ``tests/validate_configs.py`` so ``yaml.safe_load`` can parse the
# package without a real ESPHome runtime.
def _esphome_constructor(loader, node):  # type: ignore[no-untyped-def]
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


for _tag in ("!secret", "!include", "!extend", "!lambda"):
    yaml.add_constructor(_tag, _esphome_constructor, Loader=yaml.SafeLoader)


def _substitution_value(text: str, name: str) -> Optional[str]:
    """Return the right-hand value of a ``name: VALUE`` substitution line.

    Mirrors the helper in ``tests/test_core_abstract_bus.py``. Skips
    comment lines and strips trailing inline comments.
    """
    pattern = re.compile(
        rf"^\s*{re.escape(name)}:\s*(?P<value>\S+)",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        prefix = text[line_start : match.start()]
        if prefix.lstrip().startswith("#"):
            continue
        raw = match.group("value")
        if "#" in raw:
            raw = raw.split("#", 1)[0].rstrip()
        return raw.strip("\"'")
    return None


def _active_lines(text: str) -> list[str]:
    """Return only non-comment, non-blank lines from ``text``."""
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(line)
    return out


class FanRelayPackageStructureTests(unittest.TestCase):
    """``packages/expansions/fan_relay.yaml`` exists and parses as YAML."""

    def test_fan_relay_package_exists(self) -> None:
        self.assertTrue(
            FAN_RELAY_PACKAGE.is_file(),
            f"Expected the FanRelay package at {FAN_RELAY_PACKAGE} — "
            f"PACKAGE-RELAY-001 reconciles the existing file and must "
            f"not move or rename it.",
        )

    def test_fan_relay_package_parses_as_yaml(self) -> None:
        data = yaml.safe_load(FAN_RELAY_PACKAGE.read_text())
        self.assertIsInstance(
            data,
            dict,
            "fan_relay.yaml must parse as a YAML mapping (substitutions "
            "/ switch / globals / script keys).",
        )
        for key in ("substitutions", "switch"):
            self.assertIn(
                key,
                data,
                f"fan_relay.yaml must declare a top-level `{key}:` block "
                f"so downstream products can compose the FanRelay package "
                f"through substitution.",
            )


class FanRelayPinSubstitutionTests(unittest.TestCase):
    """``fan_relay_pin`` defaults to ``${relay_pin}`` and stays abstracted."""

    def test_fan_relay_pin_default_is_relay_pin_substitution(self) -> None:
        value = _substitution_value(FAN_RELAY_PACKAGE.read_text(), "fan_relay_pin")
        self.assertEqual(
            value,
            "${relay_pin}",
            "fan_relay_pin in packages/expansions/fan_relay.yaml must "
            "default to ${relay_pin} so the FanRelay package inherits "
            "whichever Core abstract package binding the parent product "
            "YAML supplies (post-CORE-ABSTRACT-BUS-001A this resolves to "
            "GPIO3, the schematic-correct Relay net per S360-100-R4 "
            "IO3).",
        )

    def test_fan_relay_pin_substitution_is_not_a_hardcoded_gpio(self) -> None:
        value = _substitution_value(FAN_RELAY_PACKAGE.read_text(), "fan_relay_pin")
        self.assertIsNotNone(
            value,
            "fan_relay_pin substitution must be present in fan_relay.yaml.",
        )
        assert value is not None  # mypy / type checker hint after assert above
        self.assertFalse(
            re.match(r"^GPIO\d+$", value),
            f"fan_relay_pin must NOT be a hard-coded GPIO (got {value!r}). "
            f"PACKAGE-RELAY-001 keeps the FanRelay package abstracted "
            f"through ${{relay_pin}}; the schematic-correct GPIO3 value "
            f"is bound by the Core abstract packages and pinned by "
            f"tests/test_core_abstract_bus.py.",
        )


class FanRelayNoHardcodedGpioTests(unittest.TestCase):
    """``fan_relay.yaml`` does not hard-code any GPIO on an active line."""

    FORBIDDEN_GPIOS = ("GPIO3", "GPIO4", "GPIO10")

    def test_fan_relay_yaml_has_no_hardcoded_specific_gpios(self) -> None:
        text = FAN_RELAY_PACKAGE.read_text()
        for line in _active_lines(text):
            for gpio in self.FORBIDDEN_GPIOS:
                self.assertNotIn(
                    gpio,
                    line,
                    f"fan_relay.yaml must not hard-code {gpio} on an "
                    f"active (non-comment) line. The Relay pin must be "
                    f"exposed through the ${{relay_pin}} / "
                    f"${{fan_relay_pin}} substitution layer so the "
                    f"package composes against any Core abstract "
                    f"package binding (post-001A the schematic-correct "
                    f"value is GPIO3, but the package must not "
                    f"hard-code it). Offending line: {line!r}",
                )

    def test_fan_relay_yaml_has_no_hardcoded_gpio_anywhere_active(self) -> None:
        text = FAN_RELAY_PACKAGE.read_text()
        pattern = re.compile(r"\bGPIO\d+\b")
        for line in _active_lines(text):
            match = pattern.search(line)
            self.assertIsNone(
                match,
                f"fan_relay.yaml must not name any GPIO on an active "
                f"(non-comment) line; the package exposes its relay "
                f"output through the substitution layer. Offending "
                f"line: {line!r}",
            )


class FanRelaySwitchUsesSubstitutionTests(unittest.TestCase):
    """The ``fan_relay_switch`` switch binds ``pin: ${fan_relay_pin}``."""

    def test_fan_relay_switch_pin_is_substitution(self) -> None:
        text = FAN_RELAY_PACKAGE.read_text()
        # Match the ``id: fan_relay_switch`` line followed by a ``pin:``
        # line that references the ``${fan_relay_pin}`` substitution
        # (the intermediate lines may include ``name:`` etc.).
        pattern = re.compile(
            r"id:\s*fan_relay_switch\s*\n"
            r"(?P<between>(?:\s*[a-z_]+:\s*[^\n]+\n)*?)"
            r"\s*pin:\s*(?P<pin>\S+)",
            re.MULTILINE,
        )
        match = pattern.search(text)
        self.assertIsNotNone(
            match,
            "Expected a `switch.platform: gpio` block declaring "
            "`id: fan_relay_switch` followed by a `pin:` line in "
            "packages/expansions/fan_relay.yaml.",
        )
        assert match is not None
        pin_value = match.group("pin").strip("\"'")
        self.assertEqual(
            pin_value,
            "${fan_relay_pin}",
            "fan_relay_switch must bind `pin: ${fan_relay_pin}` so the "
            "schematic-correct Relay net (GPIO3 per CORE-ABSTRACT-BUS-"
            "001A, inherited from the Core abstract ${relay_pin}) is "
            "consumed by downstream products through substitution. The "
            "FanRelay package must NOT name a GPIO directly.",
        )

    def test_fan_relay_switch_platform_is_gpio(self) -> None:
        data = yaml.safe_load(FAN_RELAY_PACKAGE.read_text())
        switches = data.get("switch", [])
        self.assertIsInstance(
            switches,
            list,
            "fan_relay.yaml `switch:` block must be a list of switch "
            "platforms.",
        )
        match = None
        for entry in switches:
            if isinstance(entry, dict) and entry.get("id") == "fan_relay_switch":
                match = entry
                break
        self.assertIsNotNone(
            match,
            "fan_relay.yaml must declare a switch with id "
            "`fan_relay_switch` (the FanRelay output).",
        )
        assert match is not None
        self.assertEqual(
            match.get("platform"),
            "gpio",
            "fan_relay_switch must use the `gpio` switch platform.",
        )
        self.assertEqual(
            match.get("pin"),
            "${fan_relay_pin}",
            "fan_relay_switch must bind pin: ${fan_relay_pin} so the "
            "Relay net is exposed through the substitution layer.",
        )


class CoreAbstractRelayPinCrossCheckTests(unittest.TestCase):
    """Five non-voice Core abstract packages bind ``relay_pin: GPIO3``.

    Cross-check against the schematic-correct value pinned by
    ``tests/test_core_abstract_bus.py`` ``RelayPinRebindTests``. The
    FanRelay package's ``fan_relay_pin: ${relay_pin}`` only resolves
    to the right pin if every parent Core abstract package binds
    ``relay_pin`` to ``GPIO3``.
    """

    def test_relay_pin_is_gpio3_in_every_non_voice_core_package(self) -> None:
        for pkg in NON_VOICE_CORE_PACKAGES:
            with self.subTest(package=pkg.name):
                self.assertTrue(
                    pkg.is_file(),
                    f"Expected Core abstract package at {pkg} — "
                    f"PACKAGE-RELAY-001 cross-checks against the "
                    f"post-001A relay_pin binding.",
                )
                relay = _substitution_value(pkg.read_text(), "relay_pin")
                self.assertEqual(
                    relay,
                    "GPIO3",
                    f"relay_pin in {pkg.name} must be GPIO3 (schematic "
                    f"IO3 = Relay per S360-100-R4) post-CORE-ABSTRACT-"
                    f"BUS-001A. The FanRelay package's "
                    f"fan_relay_pin: ${{relay_pin}} substitution only "
                    f"resolves to the schematic-correct pin if every "
                    f"non-voice Core abstract package binds GPIO3; got "
                    f"{relay!r}.",
                )


class VoiceCoreOutOfScopeTests(unittest.TestCase):
    """Voice-variant Core packages stay at pre-001A ``relay_pin: GPIO4``.

    Voice variants are deliberately out of scope for CORE-ABSTRACT-BUS-
    001A and for PACKAGE-RELAY-001. Their ``relay_pin`` rebind is owed
    to a later, separately-evidenced slice. This test pins the
    out-of-scope decision so the voice variants are not accidentally
    rebound under PACKAGE-RELAY-001.
    """

    def test_voice_core_relay_pin_stays_at_gpio4(self) -> None:
        for pkg in VOICE_CORE_PACKAGES:
            with self.subTest(package=pkg.name):
                if not pkg.is_file():
                    self.skipTest(f"{pkg.name} not present in repo")
                relay = _substitution_value(pkg.read_text(), "relay_pin")
                self.assertEqual(
                    relay,
                    "GPIO4",
                    f"relay_pin in {pkg.name} must remain at the "
                    f"pre-CORE-ABSTRACT-BUS-001A value GPIO4. Voice "
                    f"variants are deliberately out of scope for the "
                    f"001A rebind and for PACKAGE-RELAY-001; their "
                    f"rebind is owed to a later, separately-evidenced "
                    f"slice. Got {relay!r}.",
                )


class PackageRelayDoesNotTouchWebFlashOrProductTests(unittest.TestCase):
    """PACKAGE-RELAY-001 does not introduce any WebFlash / product file.

    PACKAGE-RELAY-001 is a package-layer reconciliation only. The
    do-not-change guardrails listed in
    ``docs/hardware/s360-310-r4-relay.md`` §[Do-not-change guardrails]
    forbid:

    * adding a Relay product YAML under ``products/`` or
      ``products/webflash/``
    * adding a ``FanRelay``-bearing entry to
      ``config/webflash-builds.json``
    * adding a ``FanRelay`` token to any Release-One config string

    These tests pin the guardrails so a future PACKAGE-RELAY-001 PR
    does not accidentally cross into the product / WebFlash / release
    layers.
    """

    def test_no_fan_relay_product_yaml(self) -> None:
        products_dir = REPO_ROOT / "products"
        if not products_dir.is_dir():
            self.skipTest("products/ directory not present in repo")
        offenders = []
        for path in products_dir.glob("**/*.yaml"):
            name = path.name.lower()
            if "fanrelay" in name or "fan-relay" in name or "fan_relay" in name:
                offenders.append(path.relative_to(REPO_ROOT))
        self.assertEqual(
            offenders,
            [],
            f"PACKAGE-RELAY-001 must not introduce a FanRelay product "
            f"YAML — that work belongs to PRODUCT-RELAY-001 and stays "
            f"separately gated. Offending paths: {offenders!r}",
        )

    def test_no_fan_relay_token_in_webflash_builds(self) -> None:
        builds = REPO_ROOT / "config" / "webflash-builds.json"
        if not builds.is_file():
            self.skipTest("config/webflash-builds.json not present in repo")
        text = builds.read_text()
        self.assertNotIn(
            "FanRelay",
            text,
            "config/webflash-builds.json must not contain the FanRelay "
            "token — PACKAGE-RELAY-001 does not advance WEBFLASH-RELAY-"
            "001 or RELEASE-RELAY-001. A FanRelay-bearing entry belongs "
            "to RELEASE-RELAY-001, not to PACKAGE-RELAY-001.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

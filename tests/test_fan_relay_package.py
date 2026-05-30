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

FW-COMPILE-RELAY-FULL-FIX-001 corrects the package after the full
compile lane (run 26334334727) failed on the FanRelay target with a
``GPIO3`` double-bind: the parent Core abstract package already declares
the ``main_relay`` ``switch.gpio`` on ``pin: ${relay_pin}``, and the
FanRelay package previously declared a *second* ``switch.gpio`` on the
same resolved pin (``${fan_relay_pin}`` defaulting to ``${relay_pin}``).
Two GPIO components on one pin fail the full ESPHome compile.

The fix de-duplicates GPIO ownership without rebinding the pin (shape C:
Core owns the GPIO output, FanRelay owns the user-facing fan switch).
``packages/expansions/fan_relay.yaml`` now exposes ``fan_relay_switch``
as a ``switch.template`` that proxies the Core ``main_relay``; it names
no GPIO and declares no ``gpio``-platform component, so the resolved
relay pin has exactly one owner (``main_relay``). ``${relay_pin}`` stays
abstract and still resolves through the Core substitution layer.

What this file checks:

  * ``packages/expansions/fan_relay.yaml`` exists and parses as YAML.
  * The package does **not** hard-code ``GPIO3`` / ``GPIO4`` /
    ``GPIO10`` (or any other ``GPIO``) on an active line — the relay
    output stays owned by the Core abstraction.
  * ``fan_relay_switch`` is a ``switch.platform: template`` that reuses
    (proxies) the Core ``main_relay`` abstraction via its
    ``turn_on_action`` / ``turn_off_action`` / ``lambda``.
  * The package declares **no** ``gpio``-platform switch or output, so
    it does not double-bind the relay pin the Core package owns.
  * The composed FanRelay product has exactly one owner of the resolved
    relay GPIO: the Core ``main_relay`` ``switch.gpio`` on
    ``${relay_pin}``.
  * The FanDAC compile-only target is left unchanged.
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
                    f"active (non-comment) line. The relay GPIO output is "
                    f"owned by the Core abstract package's `main_relay` "
                    f"`switch.gpio` on `${{relay_pin}}` (post-001A the "
                    f"schematic-correct value is GPIO3); the FanRelay "
                    f"package proxies it and must not name a GPIO. "
                    f"Offending line: {line!r}",
                )

    def test_fan_relay_yaml_has_no_hardcoded_gpio_anywhere_active(self) -> None:
        text = FAN_RELAY_PACKAGE.read_text()
        pattern = re.compile(r"\bGPIO\d+\b")
        for line in _active_lines(text):
            match = pattern.search(line)
            self.assertIsNone(
                match,
                f"fan_relay.yaml must not name any GPIO on an active "
                f"(non-comment) line; the relay output stays owned by the "
                f"Core `main_relay` abstraction. Offending line: {line!r}",
            )


class FanRelaySwitchReusesMainRelayTests(unittest.TestCase):
    """``fan_relay_switch`` is a ``template`` switch proxying ``main_relay``.

    FW-COMPILE-RELAY-FULL-FIX-001: the FanRelay package must NOT declare a
    second ``gpio``-platform switch / output on the relay pin (that
    double-binds GPIO3 with the Core ``main_relay`` and fails the full
    ESPHome compile). It instead reuses the Core relay abstraction by
    proxying ``main_relay`` through a ``switch.template``.
    """

    def _fan_relay_switch_entry(self) -> dict:
        data = yaml.safe_load(FAN_RELAY_PACKAGE.read_text())
        switches = data.get("switch", [])
        self.assertIsInstance(
            switches,
            list,
            "fan_relay.yaml `switch:` block must be a list of switch "
            "platforms.",
        )
        for entry in switches:
            if isinstance(entry, dict) and entry.get("id") == "fan_relay_switch":
                return entry
        self.fail(
            "fan_relay.yaml must declare a switch with id "
            "`fan_relay_switch` (the user-facing FanRelay control)."
        )
        raise AssertionError  # unreachable; satisfies type checker

    def test_fan_relay_switch_platform_is_template(self) -> None:
        entry = self._fan_relay_switch_entry()
        self.assertEqual(
            entry.get("platform"),
            "template",
            "fan_relay_switch must use the `template` switch platform so "
            "it proxies the Core `main_relay` rather than re-binding the "
            "relay GPIO. A `gpio`-platform switch here double-binds "
            "GPIO3 with the Core `main_relay` and fails the full compile "
            "(run 26334334727).",
        )

    def test_fan_relay_switch_does_not_bind_a_pin(self) -> None:
        entry = self._fan_relay_switch_entry()
        self.assertNotIn(
            "pin",
            entry,
            "fan_relay_switch must NOT declare a `pin:` — the relay GPIO "
            "is owned by the Core `main_relay`; the template switch only "
            "proxies it.",
        )

    def test_fan_relay_switch_proxies_main_relay(self) -> None:
        entry = self._fan_relay_switch_entry()
        rendered = yaml.safe_dump(entry)
        for action in ("turn_on_action", "turn_off_action"):
            self.assertIn(
                action,
                entry,
                f"fan_relay_switch must declare `{action}` so it proxies "
                f"the Core `main_relay` (reuses the abstraction).",
            )
        self.assertIn(
            "main_relay",
            rendered,
            "fan_relay_switch must reference `main_relay` (the Core relay "
            "abstraction) in its actions / lambda — the FanRelay layer "
            "reuses the single Core GPIO owner instead of binding its own.",
        )


class FanRelayNoGpioPlatformTests(unittest.TestCase):
    """The FanRelay package declares no ``gpio``-platform switch / output.

    This is the package-level half of the single-owner invariant: if
    ``fan_relay.yaml`` declares no ``gpio`` switch / output, then the only
    component that binds the resolved relay pin in the composed product is
    the Core ``main_relay``.
    """

    def test_no_gpio_platform_switch_or_output(self) -> None:
        data = yaml.safe_load(FAN_RELAY_PACKAGE.read_text())
        for block_key in ("switch", "output"):
            entries = data.get(block_key) or []
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                self.assertNotEqual(
                    entry.get("platform"),
                    "gpio",
                    f"fan_relay.yaml must not declare a `{block_key}.gpio` "
                    f"entry (id={entry.get('id')!r}); a second GPIO binding "
                    f"on the relay pin double-binds GPIO3 with the Core "
                    f"`main_relay`. The relay GPIO has exactly one owner.",
                )


class FanRelaySingleRelayGpioOwnerTests(unittest.TestCase):
    """Exactly one component owns the resolved relay GPIO in the product.

    The Core ceiling abstract package owns the relay GPIO as the
    ``main_relay`` ``switch.gpio`` on ``pin: ${relay_pin}``. The FanRelay
    package (above) declares no ``gpio`` component, so the composed
    FanRelay product binds the resolved relay pin exactly once.
    """

    CORE_CEILING_PACKAGE = (
        REPO_ROOT / "packages" / "hardware" / "sense360_core_ceiling.yaml"
    )

    def test_core_ceiling_main_relay_is_sole_relay_pin_gpio_owner(self) -> None:
        data = yaml.safe_load(self.CORE_CEILING_PACKAGE.read_text())
        switches = data.get("switch") or []
        gpio_relay_pin_owners = [
            entry
            for entry in switches
            if isinstance(entry, dict)
            and entry.get("platform") == "gpio"
            and entry.get("pin") == "${relay_pin}"
        ]
        self.assertEqual(
            len(gpio_relay_pin_owners),
            1,
            "sense360_core_ceiling.yaml must declare exactly one "
            "`switch.gpio` on `pin: ${relay_pin}` (the `main_relay` relay "
            f"owner); found {len(gpio_relay_pin_owners)}.",
        )
        self.assertEqual(
            gpio_relay_pin_owners[0].get("id"),
            "main_relay",
            "the sole `switch.gpio` on `${relay_pin}` in "
            "sense360_core_ceiling.yaml must be `id: main_relay`.",
        )

    def test_fan_relay_package_adds_no_relay_pin_gpio_owner(self) -> None:
        data = yaml.safe_load(FAN_RELAY_PACKAGE.read_text())
        for block_key in ("switch", "output"):
            for entry in data.get(block_key) or []:
                if not isinstance(entry, dict):
                    continue
                if entry.get("platform") == "gpio":
                    self.fail(
                        f"fan_relay.yaml `{block_key}` declares a gpio "
                        f"platform entry (id={entry.get('id')!r}); the "
                        f"FanRelay product would then have two owners of "
                        f"the resolved relay GPIO (Core `main_relay` + this "
                        f"entry). The FanRelay layer must proxy "
                        f"`main_relay`, not re-bind the pin."
                    )


class FanDacCompileOnlyTargetUnchangedTests(unittest.TestCase):
    """The FanDAC compile-only target is unchanged by the Relay fix.

    FW-COMPILE-RELAY-FULL-FIX-001 must not touch FanDAC. The FanDAC
    compile-only target stays a separate compile-only lane pointing at the
    FanDAC skeleton, distinct from the FanRelay product YAML.
    """

    COMPILE_ONLY_TARGETS = (
        REPO_ROOT / "config" / "compile-only-targets.json"
    )
    FANDAC_TARGET_ID = "ceiling-poe-fandac-compile-only"

    def setUp(self) -> None:
        import json

        if not self.COMPILE_ONLY_TARGETS.is_file():
            self.skipTest("config/compile-only-targets.json not present")
        self.doc = json.loads(self.COMPILE_ONLY_TARGETS.read_text())
        self.by_id = {
            t.get("id"): t for t in self.doc.get("targets", []) if t.get("id")
        }

    def test_fandac_compile_only_target_unchanged(self) -> None:
        target = self.by_id.get(self.FANDAC_TARGET_ID)
        self.assertIsNotNone(
            target,
            f"FanDAC compile-only target {self.FANDAC_TARGET_ID!r} must "
            "remain present and unchanged.",
        )
        assert target is not None
        self.assertEqual(
            target.get("product_yaml"),
            "products/compile-only/ceiling-poe-fandac.yaml",
            "FanDAC compile-only target must still point at the FanDAC "
            "skeleton (FW-COMPILE-RELAY-FULL-FIX-001 must not touch "
            "FanDAC).",
        )
        self.assertEqual(target.get("config_string"), "Ceiling-POE-FanDAC")
        self.assertEqual(target.get("shipment_status"), "compile-only")
        self.assertFalse(target.get("webflash_exposure_allowed_now"))


class CoreAbstractRelayPinCrossCheckTests(unittest.TestCase):
    """Five non-voice Core abstract packages bind ``relay_pin: GPIO3``.

    Cross-check against the schematic-correct value pinned by
    ``tests/test_core_abstract_bus.py`` ``RelayPinRebindTests``. The
    Core ``main_relay`` (which the FanRelay ``fan_relay_switch`` proxies)
    only resolves to the right pin if every parent Core abstract package
    binds ``relay_pin`` to ``GPIO3``.
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
    """PACKAGE-RELAY-001 does not introduce a WebFlash build / wrapper.

    PACKAGE-RELAY-001 is a package-layer reconciliation only and stays
    out of the WebFlash / release layers. PRODUCT-RELAY-001 has since
    landed a single canonical FanRelay product YAML
    (``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``) as
    an advanced / manual-warning-only sibling without any WebFlash
    exposure — that one allowed product YAML is enumerated below.

    What this class still guards:

    * No additional FanRelay product YAML may be added outside the
      single PRODUCT-RELAY-001 canonical product
      (``products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml``).
      A FanRelay WebFlash wrapper under ``products/webflash/`` is
      explicitly forbidden until ``WEBFLASH-RELAY-001`` lands.
    * No ``FanRelay`` token may appear in
      ``config/webflash-builds.json`` — PRODUCT-RELAY-001 does not add
      a build-matrix entry, and PACKAGE-RELAY-001 likewise must not.
      A ``FanRelay``-bearing build entry is owned by
      ``RELEASE-RELAY-001``.

    These tests pin both guardrails so neither slice accidentally
    crosses into the WebFlash / release layers.
    """

    # Single FanRelay product YAML allowed under products/. Anything else
    # is a guardrail violation. PRODUCT-RELAY-001 introduces exactly this
    # path; WEBFLASH-RELAY-001 (not landed) would later add a wrapper
    # under products/webflash/.
    ALLOWED_FAN_RELAY_PRODUCT_YAMLS = frozenset(
        {
            "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml",
            # The FanRelay composition (the package !include) now lives in the
            # bundle that the product shim pulls in; the bundle is the one
            # extra product-layer YAML expected to carry a FanRelay name.
            "products/bundles/ceiling-poe-ventiq-fanrelay-roomiq.yaml",
        }
    )

    def test_no_extra_fan_relay_product_yaml(self) -> None:
        products_dir = REPO_ROOT / "products"
        if not products_dir.is_dir():
            self.skipTest("products/ directory not present in repo")
        offenders = []
        for path in products_dir.glob("**/*.yaml"):
            name = path.name.lower()
            if "fanrelay" in name or "fan-relay" in name or "fan_relay" in name:
                rel = path.relative_to(REPO_ROOT).as_posix()
                if rel not in self.ALLOWED_FAN_RELAY_PRODUCT_YAMLS:
                    offenders.append(rel)
        self.assertEqual(
            offenders,
            [],
            f"Only the PRODUCT-RELAY-001 canonical FanRelay product YAMLs "
            f"{sorted(self.ALLOWED_FAN_RELAY_PRODUCT_YAMLS)!r} are allowed "
            f"under products/. A FanRelay WebFlash wrapper under "
            f"products/webflash/ requires WEBFLASH-RELAY-001 (not landed). "
            f"Offending paths: {offenders!r}",
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
            "token — neither PACKAGE-RELAY-001 nor PRODUCT-RELAY-001 "
            "advances WEBFLASH-RELAY-001 or RELEASE-RELAY-001. A "
            "FanRelay-bearing build entry belongs to RELEASE-RELAY-001.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

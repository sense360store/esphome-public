#!/usr/bin/env python3
"""CI-PIPELINE-CLARITY-001 P1 contract tests for the create-release picker.

Locks in the ``tag_suffix`` input of
``.github/workflows/create-release.yml`` as a ``type: choice`` dropdown so
an operator can no longer free-text a suffix that
``scripts/derive_release_version_channel.py`` would later reject (the
"release-input trap": a typo like ``-previw`` fails deep inside Release 3's
matrix filter with an opaque message instead of at the picker).

The invariants:

  * ``tag_suffix`` is a ``type: choice`` input (not free text).
  * Its options equal the supported non-stable suffixes: the empty option
    (blank = use the channel name) plus the recognised non-blank overrides
    ``led-preview`` and ``experimental``.
  * Every non-blank option is a recognised prerelease suffix in
    ``scripts/derive_release_version_channel.py``
    (``PRERELEASE_SUFFIX_TO_CHANNEL``), so the dropdown can never drift to a
    suffix the normalizer would reject.
  * The empty option is present and is the default (blank = channel name).

Run with::

    python3 tests/test_create_release_tag_suffix.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CREATE_RELEASE_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "create-release.yml"
)
DERIVE_SCRIPT = REPO_ROOT / "scripts" / "derive_release_version_channel.py"

# The intended non-blank dropdown options. Blank ("") is handled separately
# (it means "use the channel name", so it is not a literal suffix).
EXPECTED_NONBLANK_SUFFIXES = {"led-preview", "experimental"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _triggers(data: dict) -> dict:
    # PyYAML parses the bare key ``on:`` as boolean True (YAML 1.1 truthy key).
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {key: None for key in raw}
    if isinstance(raw, str):
        return {raw: None}
    return {}


class CreateReleaseTagSuffixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load(
            CREATE_RELEASE_WORKFLOW.read_text(encoding="utf-8")
        )
        wd = _triggers(cls.data).get("workflow_dispatch") or {}
        cls.inputs = wd.get("inputs") or {}
        cls.tag_suffix = cls.inputs.get("tag_suffix") or {}
        derive = _load_module("derive_release_version_channel", DERIVE_SCRIPT)
        # Recognised prerelease suffixes with the leading '-' stripped, e.g.
        # {"led-preview", "preview", "experimental"}.
        cls.recognised_suffixes = {
            suffix.lstrip("-")
            for suffix in derive.PRERELEASE_SUFFIX_TO_CHANNEL
        }

    def _options(self) -> list:
        return list(self.tag_suffix.get("options") or [])

    def test_tag_suffix_input_exists(self) -> None:
        self.assertIn(
            "tag_suffix",
            self.inputs,
            "create-release.yml must keep a tag_suffix workflow_dispatch input",
        )

    def test_tag_suffix_is_type_choice(self) -> None:
        self.assertEqual(
            self.tag_suffix.get("type"),
            "choice",
            "create-release.yml tag_suffix must be a `type: choice` dropdown "
            "(CI-PIPELINE-CLARITY-001 P1) so an operator cannot free-text a "
            "suffix that derive_release_version_channel.py would reject",
        )

    def test_tag_suffix_options_equal_supported_nonstable_suffixes(self) -> None:
        options = self._options()
        normalized = {str(opt) for opt in options}
        expected = {""} | EXPECTED_NONBLANK_SUFFIXES
        self.assertEqual(
            normalized,
            expected,
            f"create-release.yml tag_suffix options {options!r} must equal the "
            f"supported non-stable suffixes {sorted(expected)!r} (empty = use "
            "the channel name; led-preview and experimental are the explicit "
            "non-blank overrides)",
        )

    def test_tag_suffix_includes_blank_option(self) -> None:
        options = [str(opt) for opt in self._options()]
        self.assertIn(
            "",
            options,
            "create-release.yml tag_suffix must offer the blank option so the "
            "operator can fall back to the channel name (stable -> plain "
            "vX.Y.Z), which is the documented default",
        )

    def test_tag_suffix_defaults_to_blank(self) -> None:
        self.assertEqual(
            str(self.tag_suffix.get("default", "")),
            "",
            "create-release.yml tag_suffix default must be the blank option "
            "(blank = use the channel name)",
        )

    def test_nonblank_options_are_recognised_prerelease_suffixes(self) -> None:
        # Integrity: every non-blank option must be a suffix
        # derive_release_version_channel.py actually recognises, so the picker
        # can never advertise a suffix the normalizer would reject.
        for opt in self._options():
            text = str(opt)
            if text == "":
                continue
            self.assertIn(
                text,
                self.recognised_suffixes,
                f"tag_suffix option {text!r} is not a recognised prerelease "
                f"suffix in derive_release_version_channel.py "
                f"({sorted(self.recognised_suffixes)!r}); the dropdown must "
                "not offer a suffix the normalizer rejects",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

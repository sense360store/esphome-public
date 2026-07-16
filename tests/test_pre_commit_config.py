#!/usr/bin/env python3
"""Regression tests for ``.pre-commit-config.yaml`` parseability.

REPO-VALIDATION-BASELINE-REPAIR-001: the yamllint hook's ``--config-data``
argument is a single CLI string whose value contains ``: `` pairs. Written
as an unquoted plain scalar it is invalid YAML ("mapping values are not
allowed here"), which broke ``pre-commit validate-config`` and every
``pre-commit run``. These tests pin that the file stays parseable by
PyYAML's safe loader and that the yamllint hook keeps the exact semantic
configuration it has always carried (extends default; line-length max 120;
comments min-spaces-from-content 1; document-start disabled; truthy
check-keys off) — matching ``.yamllint`` at the repo root.

Uses Python's stdlib unittest (matching this repo's no-pytest convention
for Python validators). Run with::

    python3 tests/test_pre_commit_config.py
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / ".pre-commit-config.yaml"

EXPECTED_YAMLLINT_CONFIG = {
    "extends": "default",
    "rules": {
        "line-length": {"max": 120},
        "comments": {"min-spaces-from-content": 1},
        "document-start": "disable",
        "truthy": {"check-keys": False},
    },
}


def _load_config():
    with CONFIG_PATH.open() as handle:
        return yaml.safe_load(handle)


def _yamllint_hook(config):
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []) or []:
            if hook.get("id") == "yamllint":
                return hook
    return None


class PreCommitConfigParseTests(unittest.TestCase):
    """The pre-commit config must stay valid YAML under the safe loader."""

    def test_file_exists(self):
        self.assertTrue(CONFIG_PATH.is_file())

    def test_parses_with_safe_load(self):
        # This is exactly what pre-commit itself does; an unquoted
        # colon-bearing scalar anywhere in the file breaks it.
        config = _load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("repos", config)

    def test_all_hook_args_are_strings(self):
        # A mis-quoted arg would parse as a dict/list instead of the
        # single CLI string pre-commit passes through to the tool.
        config = _load_config()
        for repo in config.get("repos", []):
            for hook in repo.get("hooks", []) or []:
                for arg in hook.get("args", []) or []:
                    self.assertIsInstance(
                        arg,
                        str,
                        f"hook {hook.get('id')!r} arg {arg!r} is not a string",
                    )


class YamllintHookSemanticsTests(unittest.TestCase):
    """The yamllint hook keeps its exact logical configuration."""

    def setUp(self):
        self.hook = _yamllint_hook(_load_config())
        self.assertIsNotNone(self.hook, "yamllint hook missing")

    def _config_data_arg(self):
        args = self.hook.get("args", []) or []
        matches = [a for a in args if a.startswith("--config-data=")]
        self.assertEqual(
            len(matches), 1, f"expected exactly one --config-data arg, got {args!r}"
        )
        return matches[0]

    def test_config_data_value_is_valid_yaml(self):
        value = self._config_data_arg().split("=", 1)[1]
        parsed = yaml.safe_load(value)
        self.assertIsInstance(parsed, dict)

    def test_config_data_semantics_unchanged(self):
        value = self._config_data_arg().split("=", 1)[1]
        self.assertEqual(yaml.safe_load(value), EXPECTED_YAMLLINT_CONFIG)

    def test_parsable_format_arg_retained(self):
        self.assertIn("--format=parsable", self.hook.get("args", []) or [])

    def test_targets_yaml_files(self):
        self.assertEqual(self.hook.get("files"), r"\.(yaml|yml)$")


if __name__ == "__main__":
    unittest.main()

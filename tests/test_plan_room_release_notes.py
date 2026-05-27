#!/usr/bin/env python3
"""Unit tests for scripts/plan_room_release_notes.py (RELEASE-NOTES-PIPELINE-001).

Uses Python's stdlib ``unittest`` (matching the no-pytest convention the
rest of the validators in this repo use). Run with:

    python3 tests/test_plan_room_release_notes.py

The tests lock in the RELEASE-NOTES-PIPELINE-001 contract:

  * the dry-run plan includes the stable RoomIQ build and the preview LED
    build, with their channel labels and YAML paths;
  * the plan excludes the FanRelay / FanPWM / FanDAC manual candidates from
    the release-eligible section (they appear only under "explicitly
    excluded");
  * the plan makes no hardware-stable / compliance claim beyond the catalog's
    recorded ``hardware_status``;
  * the guardrail refuses any fan candidate that leaks into the release
    matrix;
  * the planner is dry-run only and never writes firmware/sources.json or
    manifest.json.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "plan_room_release_notes.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


plan = _load_module("plan_room_release_notes", SCRIPT_PATH)

STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
STABLE_YAML = "products/sense360-ceiling-poe-ventiq-roomiq.yaml"
LED_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
LED_YAML = "products/sense360-ceiling-poe-ventiq-roomiq-led.yaml"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")
# Affirmative readiness claims the plan must never make about fan candidates
# (or beyond the catalog's recorded state for the room builds).
FORBIDDEN_CLAIMS = (
    "compliant",
    "certified",
    "compliance approved",
    "compliance-approved",
    "ce marked",
    "ul listed",
)


def _plan(commit: str = "deadbeef"):
    return plan.build_plan(commit=commit)


def _render(commit: str = "deadbeef") -> str:
    return plan.render_markdown(_plan(commit=commit))


class ReleaseEligibleBuildsTests(unittest.TestCase):
    def test_plan_has_exactly_the_two_release_builds(self) -> None:
        builds = _plan()["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {STABLE_CONFIG, LED_CONFIG})

    def test_includes_stable_roomiq(self) -> None:
        builds = {b["config_string"]: b for b in _plan()["builds"]}
        self.assertIn(STABLE_CONFIG, builds)
        self.assertEqual(builds[STABLE_CONFIG]["channel"], "stable")
        self.assertEqual(builds[STABLE_CONFIG]["validation_errors"], [])

    def test_includes_preview_led(self) -> None:
        builds = {b["config_string"]: b for b in _plan()["builds"]}
        self.assertIn(LED_CONFIG, builds)
        self.assertEqual(builds[LED_CONFIG]["channel"], "preview")
        self.assertEqual(builds[LED_CONFIG]["validation_errors"], [])

    def test_render_includes_channel_labels(self) -> None:
        text = _render()
        self.assertIn("`stable`", text)
        self.assertIn("`preview`", text)

    def test_render_includes_yaml_paths(self) -> None:
        text = _render()
        self.assertIn(STABLE_YAML, text)
        self.assertIn(LED_YAML, text)

    def test_render_includes_config_strings(self) -> None:
        text = _render()
        self.assertIn(STABLE_CONFIG, text)
        self.assertIn(LED_CONFIG, text)

    def test_render_includes_artifact_names(self) -> None:
        text = _render()
        self.assertIn("Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin", text)
        self.assertIn(
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-v1.0.0-preview.bin", text
        )

    def test_render_includes_pinned_source_yaml_urls(self) -> None:
        text = _render(commit="abc123")
        self.assertIn("/blob/v1.0.0/" + STABLE_YAML, text)
        self.assertIn("/blob/abc123/" + STABLE_YAML, text)

    def test_render_records_esphome_and_commit(self) -> None:
        text = _render(commit="abc123")
        self.assertIn("abc123", text)
        # ESPHome version is read from the release workflow.
        self.assertIn(_plan()["esphome_version"], text)


class FanExclusionTests(unittest.TestCase):
    def _split_sections(self, text: str):
        marker = "## Explicitly excluded"
        self.assertIn(marker, text, "plan must have an explicit-exclusions section")
        head, _, tail = text.partition(marker)
        return head, tail

    def test_fans_absent_from_release_section(self) -> None:
        head, _ = self._split_sections(_render())
        for token in FAN_TOKENS:
            self.assertNotIn(
                token,
                head,
                f"{token} must not appear in the release-eligible section",
            )

    def test_fans_present_in_exclusions_section(self) -> None:
        _, tail = self._split_sections(_render())
        for token in FAN_TOKENS:
            self.assertIn(
                token,
                tail,
                f"{token} must be listed under explicitly excluded",
            )

    def test_fan_candidates_not_release_builds(self) -> None:
        configs = {b["config_string"] for b in _plan()["builds"]}
        for token in FAN_TOKENS:
            self.assertFalse(
                any(token.lower() in c.lower() for c in configs),
                f"{token} must not be a release-eligible build",
            )

    def test_guardrail_refuses_fan_in_release_matrix(self) -> None:
        rogue_builds = [
            {
                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "product_yaml": "products/webflash/x.yaml",
            }
        ]
        with self.assertRaises(plan.PlanError) as ctx:
            plan._assert_no_fan_in_release(rogue_builds, [])
        self.assertIn("FanRelay", str(ctx.exception))

    def test_guardrail_refuses_fan_product_yaml(self) -> None:
        fan_candidates = [
            {
                "family": "FanPWM",
                "product_yaml": "products/sense360-ceiling-poe-fanpwm.yaml",
            }
        ]
        rogue_builds = [
            {
                "config_string": "Ceiling-POE-Mystery",
                "product_yaml": "products/sense360-ceiling-poe-fanpwm.yaml",
            }
        ]
        with self.assertRaises(plan.PlanError):
            plan._assert_no_fan_in_release(rogue_builds, fan_candidates)


class NoOverclaimTests(unittest.TestCase):
    def test_uses_catalog_hardware_status_verbatim(self) -> None:
        text = _render()
        self.assertIn("verified-for-release-one", text)
        self.assertIn("verified-led-candidate", text)

    def test_disclaims_hardware_and_compliance_claims(self) -> None:
        for build in _plan()["builds"]:
            joined = " ".join(build["known_limitations"]).lower()
            self.assertIn("no hardware-stability or compliance claim", joined)

    def test_no_affirmative_compliance_or_certification_claim(self) -> None:
        lowered = _render().lower()
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(
                claim,
                lowered,
                f"plan must not assert {claim!r}",
            )

    def test_fan_exclusions_disclaim_readiness(self) -> None:
        _, tail = _render().partition("## Explicitly excluded")[0::2]
        lowered = tail.lower()
        self.assertIn("not", lowered)
        self.assertIn("no webflash exposure", lowered)
        self.assertIn("hardware-pending", lowered)


class DryRunSafetyTests(unittest.TestCase):
    def test_main_writes_only_requested_output(self) -> None:
        sources = REPO_ROOT / "firmware" / "sources.json"
        manifest = REPO_ROOT / "manifest.json"
        sources_before = sources.exists()
        manifest_before = manifest.exists()

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "plan.md"
            rc = plan.main(["--output", str(out), "--commit", "deadbeef"])
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())
            content = out.read_text(encoding="utf-8")
            self.assertIn("DRY RUN", content)
            self.assertIn(STABLE_CONFIG, content)

        # The planner must never create release-publish side-effect files.
        self.assertEqual(sources.exists(), sources_before)
        self.assertEqual(manifest.exists(), manifest_before)

    def test_plan_announces_dry_run(self) -> None:
        self.assertIn("Dry run only", _render())


if __name__ == "__main__":
    unittest.main(verbosity=2)

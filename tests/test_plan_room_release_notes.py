#!/usr/bin/env python3
"""Unit tests for scripts/plan_room_release_notes.py (RELEASE-NOTES-PIPELINE-001).

Uses Python's stdlib ``unittest`` (matching the no-pytest convention the
rest of the validators in this repo use). Run with:

    python3 tests/test_plan_room_release_notes.py

The tests lock in the RELEASE-NOTES-PIPELINE-001 contract, as revised by
owner decision HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09):

  * the dry-run plan includes the stable RoomIQ build and the preview LED
    build, with their channel labels and YAML paths;
  * fan-token builds (FanRelay / FanPWM / FanDAC) are release-eligible on
    non-stable channels only: FanRelay exactly ``experimental``, FanPWM /
    FanDAC exactly ``preview`` — never ``stable``;
  * the manual candidates in config/manual-firmware-artifacts.json remain a
    parallel point-to-point lane and appear under "manual-lane candidates";
  * the plan makes no hardware-stable / compliance claim beyond the catalog's
    recorded ``hardware_status``;
  * the guardrail refuses any fan-token build row on the stable channel (or
    any channel other than the family's approved one), and refuses a release
    row whose product_yaml is a manual candidate's canonical YAML;
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
# HW-RELEASE-001 channel teeth: the only channel each fan family may
# release on. Never "stable".
FAN_ALLOWED_CHANNELS = {
    "FanRelay": "experimental",
    "FanPWM": "preview",
    "FanDAC": "preview",
}
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
    def test_plan_has_exactly_the_release_eligible_builds(self) -> None:
        # RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001 added three room-bundle
        # preview build rows; TRIAC-COMMISSIONING-001 then added the experimental
        # self-build mains FanTRIAC build (channel experimental).
        # CI-PIPELINE-CLARITY-001 P4a then DE-LISTED Ceiling-POE-RoomIQ-LED
        # (never built or served), removing its build row. Owner decision
        # HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) then re-listed
        # Ceiling-POE-RoomIQ-LED and added the six FanPWM / FanDAC preview
        # rows and the two FanRelay experimental rows. The plan now covers
        # fourteen release-eligible builds.
        builds = _plan()["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(
            configs,
            {
                STABLE_CONFIG,
                LED_CONFIG,
                "Ceiling-POE-AirIQ-RoomIQ",
                "Ceiling-POE-RoomIQ",
                "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
                "Ceiling-POE-RoomIQ-LED",
                "Ceiling-POE-FanPWM",
                "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
                "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
                "Ceiling-POE-FanDAC",
                "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
                "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
                "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
                "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
            },
        )

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
        # Derive the expected artifact names from the plan rows so release
        # version bumps do not rot this test.
        builds = {b["config_string"]: b for b in _plan()["builds"]}
        text = _render()
        self.assertIn(builds[STABLE_CONFIG]["artifact_name"], text)
        self.assertIn(builds[LED_CONFIG]["artifact_name"], text)
        self.assertTrue(builds[STABLE_CONFIG]["artifact_name"].endswith("-stable.bin"))
        self.assertTrue(builds[LED_CONFIG]["artifact_name"].endswith("-preview.bin"))

    def test_render_includes_pinned_source_yaml_urls(self) -> None:
        builds = {b["config_string"]: b for b in _plan(commit="abc123")["builds"]}
        stable_version = builds[STABLE_CONFIG]["version"]
        text = _render(commit="abc123")
        self.assertIn(f"/blob/v{stable_version}/" + STABLE_YAML, text)
        self.assertIn("/blob/abc123/" + STABLE_YAML, text)

    def test_render_records_esphome_and_commit(self) -> None:
        text = _render(commit="abc123")
        self.assertIn("abc123", text)
        # ESPHome version is read from the release workflow.
        self.assertIn(_plan()["esphome_version"], text)


class FanChannelGuardrailTests(unittest.TestCase):
    """HW-RELEASE-001: fan builds release on non-stable channels only."""

    def _split_sections(self, text: str):
        marker = "## Manual-lane candidates"
        self.assertIn(marker, text, "plan must have a manual-lane section")
        head, _, tail = text.partition(marker)
        return head, tail

    def test_fan_builds_present_in_release_section(self) -> None:
        # HW-RELEASE-001 made fan configs release-eligible; they now appear
        # in the release-eligible section (on non-stable channels).
        head, _ = self._split_sections(_render())
        for token in FAN_TOKENS:
            self.assertIn(
                token,
                head,
                f"{token} builds must appear in the release-eligible section",
            )

    def test_fans_present_in_manual_lane_section(self) -> None:
        # The manual lane persists as a parallel point-to-point path.
        _, tail = self._split_sections(_render())
        for token in FAN_TOKENS:
            self.assertIn(
                token,
                tail,
                f"{token} must be listed under manual-lane candidates",
            )

    def test_fan_builds_never_stable(self) -> None:
        for build in _plan()["builds"]:
            cs = build["config_string"]
            for token, allowed in FAN_ALLOWED_CHANNELS.items():
                if token.lower() in cs.lower():
                    self.assertNotEqual(
                        build["channel"],
                        "stable",
                        f"{cs} carries {token}; must never be stable",
                    )
                    self.assertEqual(
                        build["channel"],
                        allowed,
                        f"{cs} carries {token}; channel must be exactly "
                        f"{allowed!r}",
                    )

    def test_guardrail_refuses_fan_on_stable_channel(self) -> None:
        rogue_builds = [
            {
                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "product_yaml": "products/webflash/x.yaml",
                "channel": "stable",
            }
        ]
        with self.assertRaises(plan.PlanError) as ctx:
            plan._assert_no_fan_in_release(rogue_builds, [])
        self.assertIn("FanRelay", str(ctx.exception))
        self.assertIn("HW-RELEASE-001", str(ctx.exception))

    def test_guardrail_refuses_fanrelay_outside_experimental(self) -> None:
        # FanRelay is mains-adjacent: exactly "experimental", not "preview".
        rogue_builds = [
            {
                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "product_yaml": "products/webflash/x.yaml",
                "channel": "preview",
            }
        ]
        with self.assertRaises(plan.PlanError):
            plan._assert_no_fan_in_release(rogue_builds, [])

    def test_guardrail_refuses_fanpwm_outside_preview(self) -> None:
        # FanPWM / FanDAC are SELV preview-lane: exactly "preview".
        rogue_builds = [
            {
                "config_string": "Ceiling-POE-FanPWM",
                "product_yaml": "products/webflash/x.yaml",
                "channel": "experimental",
            }
        ]
        with self.assertRaises(plan.PlanError):
            plan._assert_no_fan_in_release(rogue_builds, [])

    def test_guardrail_allows_fans_on_approved_channels(self) -> None:
        ok_builds = [
            {
                "config_string": "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
                "product_yaml": "products/webflash/a.yaml",
                "channel": "experimental",
            },
            {
                "config_string": "Ceiling-POE-FanPWM",
                "product_yaml": "products/webflash/b.yaml",
                "channel": "preview",
            },
            {
                "config_string": "Ceiling-POE-FanDAC",
                "product_yaml": "products/webflash/c.yaml",
                "channel": "preview",
            },
        ]
        # Must not raise.
        plan._assert_no_fan_in_release(ok_builds, [])

    def test_guardrail_refuses_fan_product_yaml(self) -> None:
        # A release row must never point at a manual candidate's canonical
        # top-level product YAML (release rows use products/webflash/
        # wrappers) — kept from the pre-HW-RELEASE-001 guardrail.
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
                "channel": "preview",
            }
        ]
        with self.assertRaises(plan.PlanError):
            plan._assert_no_fan_in_release(rogue_builds, fan_candidates)


class NoOverclaimTests(unittest.TestCase):
    def test_uses_catalog_hardware_status_verbatim(self) -> None:
        text = _render()
        self.assertIn("verified-for-release-one", text)
        self.assertIn("verified-led-candidate", text)
        # HW-RELEASE-001: the nine owner-declared rows carry the catalog's
        # hardware_status verbatim — an owner declaration, not bench proof.
        self.assertIn("owner-declared-bench-working-hw-release-001", text)

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

    def test_fan_manual_lane_disclaims_readiness(self) -> None:
        # HW-RELEASE-001: the manual-lane section must still make the
        # channel teeth and the owner-declared (not bench-proven) posture
        # explicit for fan builds.
        _, tail = _render().partition("## Manual-lane candidates")[0::2]
        lowered = tail.lower()
        self.assertIn("never", lowered)
        self.assertIn("non-stable channels only", lowered)
        self.assertIn("owner-declared", lowered)
        self.assertIn("not bench", lowered)


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

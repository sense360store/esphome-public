#!/usr/bin/env python3
"""Zero-alias ledger (SENSE360-CANONICALISATION-001 PR 07).

The charter's deletion policy ("zero legacy aliases") and the owner
instruction of 2026-07-28 removed every legacy alias, naming shim and
duplicate include chain in the hardware layer after re-pointing each live
consumer to the authoritative board package. The PR 06 contract freshness
gate proved every resolved board composition byte-identical across the
removal.

fan_pwm.yaml is deliberately NOT in this ledger: it composes the sx1509
binding layer AND declares the four fan speed controllers, so it is
authoritative, not an alias (an early PR 07 classification error caught
and reverted before commit).

This module replaces the four alias-pinning test files
(test_airiq_alias_packages, test_roomiq_alias_packages,
test_ventiq_alias_packages, test_fandac_alias_packages) and the per-family
"legacy paths still resolve" assertions, whose premise the zero-alias
decision inverted: the deleted paths must now STAY deleted, and nothing may
include them again. Deleting the old guards without this inverted ledger
would have left the return path unguarded.

Evidence ceiling: static inspection only. Release tags keep every historical
path; nothing published changes.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Every hardware-layer path PR 07 deleted. Each entry names its disposition
# basis; the authoritative successor is what consumers were re-pointed to.
DELETED_PATHS = {
    # Naming / legacy aliases of board packages (successor in parentheses).
    "packages/expansions/airiq.yaml": "alias of packages/boards/s360-210-airiq.yaml",
    "packages/expansions/airiq_ceiling.yaml": "alias of packages/boards/s360-210-airiq.yaml",
    "packages/expansions/airiq_ceiling_s3.yaml": "alias of packages/boards/s360-210-airiq-ceiling-s3.yaml",
    "packages/expansions/airiq_bathroom_base.yaml": "alias of packages/boards/s360-211-ventiq.yaml",
    "packages/expansions/ventiq.yaml": "alias chain to packages/boards/s360-211-ventiq.yaml",
    "packages/expansions/roomiq.yaml": "alias chain to packages/boards/s360-200-roomiq-climate.yaml",
    "packages/expansions/roomiq_radar.yaml": "alias chain to packages/boards/s360-200-roomiq-radar.yaml",
    "packages/expansions/comfort_ceiling.yaml": "alias of packages/boards/s360-200-roomiq-climate.yaml",
    "packages/expansions/presence_ceiling.yaml": "alias of packages/boards/s360-200-roomiq-radar.yaml",
    "packages/expansions/bathroom.yaml": "composite alias (VentIQ board + legacy bathroom profile)",
    "packages/expansions/fan_dac.yaml": "alias of packages/expansions/fan_gp8403.yaml",
    "packages/hardware/power_poe.yaml": "alias of packages/boards/s360-410-poe-psu.yaml",
    "packages/hardware/led_ring_ceiling.yaml": "alias of packages/boards/s360-300-led.yaml",
    # The undocumented led-mic pair: neither half was ever documented,
    # advertised or published as a customer entrypoint (the owner evidence
    # test of 2026-07-28), so both halves were internal and removable. The
    # S360-LED-V-C hardware question stays owned by the hardware catalogue,
    # which lists no such board.
    "packages/hardware/led_ring_mic_ceiling.yaml": "undocumented pair, deleted whole",
    "packages/boards/s360-300-led-mic-ceiling.yaml": "undocumented pair, deleted whole",
    # Feature-layer naming aliases with no consumer.
    "packages/features/roomiq_profile.yaml": "alias of the comfort profile chain",
    "packages/features/roomiq_radar_profile.yaml": "alias of the presence profile chain",
    "packages/features/ventiq_profile.yaml": "alias of the bathroom profile chain",
    "packages/features/airiq_profile.yaml": "alias of the airiq basic profile",
    "packages/features/airiq_auto_ventilation_profile.yaml": "alias of the auto-ventilation profile",
    "packages/features/airiq_extended_profile.yaml": "alias of the extended profile",
    "packages/features/airiq_mqtt_profile.yaml": "alias of the mqtt profile",
    # PR 07 packages/remote resolution (owner evidence test).
    "packages/remote/blower-framework.yaml": "unpublished remainder of packages/remote/",
}

SCAN_DIRS = ("products", "packages")


class ZeroAliasLedgerTests(unittest.TestCase):
    """Deleted paths stay deleted, and nothing includes them again."""

    def test_every_deleted_path_stays_deleted(self):
        for rel in DELETED_PATHS:
            self.assertFalse(
                (REPO_ROOT / rel).exists(),
                f"{rel} was deleted under SENSE360-CANONICALISATION-001 PR 07 "
                f"({DELETED_PATHS[rel]}) and must not return; compose the "
                "authoritative board package instead",
            )

    def test_no_yaml_includes_a_deleted_path(self):
        basenames = {Path(rel).name: rel for rel in DELETED_PATHS}
        offenders = []
        for scan in SCAN_DIRS:
            for path in (REPO_ROOT / scan).rglob("*.yaml"):
                for line in path.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#") or "!include" not in stripped:
                        continue
                    for base, rel in basenames.items():
                        if stripped.endswith("/" + base) or stripped.endswith(
                            " " + base
                        ):
                            offenders.append(
                                f"{path.relative_to(REPO_ROOT)}: includes deleted {rel}"
                            )
        self.assertEqual(offenders, [])

    def test_the_ledger_is_not_silently_shrunk(self):
        """Removing an entry here needs the same deliberateness as a revert."""
        self.assertGreaterEqual(len(DELETED_PATHS), 23)


if __name__ == "__main__":
    unittest.main()

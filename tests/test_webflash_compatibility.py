#!/usr/bin/env python3
"""Validate the local WebFlash compatibility snapshot.

The snapshot at ``config/webflash-compatibility.json`` is a repo-local
mirror of the WebFlash product contract. WebFlash remains the upstream
source of truth; this file just lets validators and CI enforce the same
naming rules without fetching WebFlash.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"


def _load_snapshot():
    with open(SNAPSHOT_PATH, "r") as f:
        return json.load(f)


def test_snapshot_file_exists():
    assert SNAPSHOT_PATH.is_file(), f"Missing snapshot at {SNAPSHOT_PATH}"


def test_snapshot_parses_as_json():
    data = _load_snapshot()
    assert isinstance(data, dict)


def test_schema_version_is_one():
    data = _load_snapshot()
    assert data["schema_version"] == 1


def test_source_is_webflash():
    data = _load_snapshot()
    assert data["source"] == "WebFlash"


def test_ceiling_is_allowed_mounting():
    data = _load_snapshot()
    assert "Ceiling" in data["canonical_mounting"]


def test_poe_is_allowed_power():
    data = _load_snapshot()
    assert "POE" in data["canonical_power"]


def test_fantriac_is_allowed_module():
    data = _load_snapshot()
    assert "FanTRIAC" in data["canonical_modules"]


def test_generic_fan_token_is_forbidden():
    data = _load_snapshot()
    assert "Fan" in data["forbidden_tokens"]


def test_legacy_tokens_are_forbidden():
    data = _load_snapshot()
    for token in ("Bathroom", "Comfort", "Presence"):
        assert (
            token in data["forbidden_tokens"]
        ), f"Expected legacy token '{token}' in forbidden_tokens"


def test_release_one_required_config_present():
    data = _load_snapshot()
    assert "Ceiling-POE-VentIQ-RoomIQ" in data["release_one_required_configs"]


def test_artifact_pattern_matches_contract():
    data = _load_snapshot()
    assert (
        data["artifact_pattern"] == "Sense360-{CONFIG_STRING}-v{VERSION}-{CHANNEL}.bin"
    )


def test_roomiq_can_pair_with_ventiq():
    data = _load_snapshot()
    assert data["rules"]["roomiq_can_pair_with_ventiq"] is True


def test_airiq_and_ventiq_are_mutually_exclusive():
    data = _load_snapshot()
    rules = data["rules"]
    assert "airiq_and_ventiq_mutually_exclusive" in rules
    assert rules["airiq_and_ventiq_mutually_exclusive"] is True


# ---------------------------------------------------------------------------
# COMPAT-001 drift-protection tests.
#
# These tests lock the current taxonomy invariants documented in
# docs/webflash-compatibility-taxonomy-audit.md. They pass against the
# current config/webflash-compatibility.json without any change to that
# file; they only prevent silent drift in a later PR.
# ---------------------------------------------------------------------------


def test_led_is_canonical_module():
    """LED stays in canonical_modules as a reserved future token.

    See docs/webflash-compatibility-taxonomy-audit.md: LED is a known
    WebFlash module but is excluded from Release-One because the
    Ceiling-POE-VentIQ-RoomIQ config string carries no LED token. The
    token must remain in the taxonomy so future LED-bearing configs
    (e.g. Ceiling-POE-VentIQ-RoomIQ-LED) parse correctly.
    """
    data = _load_snapshot()
    assert "LED" in data["canonical_modules"]


def test_all_four_fan_driver_tokens_are_canonical_modules():
    """All four fan-driver tokens stay in canonical_modules.

    Dropping any of FanRelay / FanPWM / FanDAC / FanTRIAC would break the
    fan-driver "max one of" policy and Sense360 driver coverage. See
    docs/webflash-contract.md §5 and docs/webflash-compatibility-taxonomy-audit.md.
    """
    data = _load_snapshot()
    for token in ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC"):
        assert (
            token in data["canonical_modules"]
        ), f"Expected fan-driver token '{token}' in canonical_modules"


def test_canonical_mounting_is_ceiling_only():
    """canonical_mounting must be exactly ['Ceiling'].

    Release-One supports Ceiling only; the legacy Wall mount must not
    silently re-enter the WebFlash taxonomy. See
    docs/webflash-contract.md §3.
    """
    data = _load_snapshot()
    assert data["canonical_mounting"] == ["Ceiling"]


def test_canonical_power_is_usb_poe_pwr_only():
    """canonical_power must be exactly ['USB', 'POE', 'PWR'].

    Pins the power-token set against silent additions or removals. See
    docs/webflash-contract.md §3.
    """
    data = _load_snapshot()
    assert data["canonical_power"] == ["USB", "POE", "PWR"]


def test_production_channel_is_stable():
    """production_channel must remain 'stable'.

    Release-One ships on the stable channel; preview and beta are
    user-opt-in. See docs/webflash-contract.md §1.
    """
    data = _load_snapshot()
    assert data["production_channel"] == "stable"


def test_fan_analog_is_forbidden():
    """FanAnalog must stay in forbidden_tokens.

    FanAnalog is the legacy alias for FanDAC; dropping it from
    forbidden_tokens would weaken the alias guard. See
    docs/webflash-contract.md §3.
    """
    data = _load_snapshot()
    assert "FanAnalog" in data["forbidden_tokens"]


def _run_all():
    tests = [
        test_snapshot_file_exists,
        test_snapshot_parses_as_json,
        test_schema_version_is_one,
        test_source_is_webflash,
        test_ceiling_is_allowed_mounting,
        test_poe_is_allowed_power,
        test_fantriac_is_allowed_module,
        test_generic_fan_token_is_forbidden,
        test_legacy_tokens_are_forbidden,
        test_release_one_required_config_present,
        test_artifact_pattern_matches_contract,
        test_roomiq_can_pair_with_ventiq,
        test_airiq_and_ventiq_are_mutually_exclusive,
        test_led_is_canonical_module,
        test_all_four_fan_driver_tokens_are_canonical_modules,
        test_canonical_mounting_is_ceiling_only,
        test_canonical_power_is_usb_poe_pwr_only,
        test_production_channel_is_stable,
        test_fan_analog_is_forbidden,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    import sys

    sys.exit(1 if _run_all() else 0)

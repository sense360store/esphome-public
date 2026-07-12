#!/usr/bin/env python3
"""Bench host helper — SPIKE-PROVISIONING-BENCH-001 (SEC-ESP-PROVISIONING-001).

TEST-ONLY — NOT FOR RELEASE OR CUSTOMER USE

BENCH-ONLY WARNING: this tool exists solely so the owner can drive the
approved bench procedure (docs/hardware/SPIKE-PROVISIONING-BENCH-001-
procedure.md, draft PR #822) against the bench spike harness
(bench-spike.yaml). It talks to the device exclusively through the stock
ESPHome native API via aioesphomeapi — no custom protocol, no cloud, no
browser dependency, no telemetry.

Credential rules:

* every credential is a THROWAWAY bench value, generated at execution time
  (``gen-key``) or supplied by the operator at the prompt / on stdin;
* nothing is committed, nothing is written to disk by this tool;
* no credential value is ever printed or logged — only lengths and
  set/unset states. The one deliberate exception is ``gen-key`` (below),
  whose entire purpose is to hand the operator a fresh key to record as
  bench evidence per procedure V-01 step 3.

Destructive operations (``reset-test``) require typed confirmation.

Commands (see ``--help`` for arguments):

  gen-key       generate a fresh throwaway 32-byte base64 noise key (prints
                it — this is the ONE intended credential output, per
                procedure V-01 step 3 "record it in the evidence")
  set-api-key   send NoiseEncryptionSetKeyRequest with a throwaway key
                (V-01 step 4; key read from prompt or --key-env)
  set-ota-password / set-ap-password
                call the harness bench_set_* action with a throwaway value
                read from an interactive prompt (H-02 / H-03)
  set-record    write the synthetic persistence record (H-04, V-03)
  clear-record  clear the synthetic persistence record
  inspect       connect and print the non-secret diagnostic entity states
                (H-05): key/password set-states, record validity, boot
                count, reset reason, MAC, harness identity
  reboot-test   press the harness restart button, wait, reconnect, and
                print the diagnostics again (persistence-across-reboot leg)
  reset-test    press the stock factory-reset button (FULL NVS ERASE) —
                requires typing the confirmation phrase

Requires: python3 >= 3.10, aioesphomeapi (bench host pins the version in
the validation record; the ADR desk evidence used 45.6.0).
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import getpass
import os
import secrets as _secrets
import sys

try:
    import aioesphomeapi
except ImportError:  # pragma: no cover - bench-host dependency, not CI's
    aioesphomeapi = None

RESET_CONFIRMATION = "ERASE ALL BENCH STATE"

# Non-secret diagnostic entities exposed by bench-spike.yaml (H-05).
DIAGNOSTIC_OBJECT_IDS = (
    "bench_esphome_version",
    "bench_device_mac",
    "bench_reset_reason",
    "bench_harness_identity",
    "bench_api_key_state",
    "bench_ota_password_state",
    "bench_ap_password_state",
    "bench_persistence_state",
    "bench_record_valid",
    "bench_record_present",
    "bench_boot_count",
)


def _require_aioesphomeapi() -> None:
    if aioesphomeapi is None:
        sys.exit(
            "aioesphomeapi is not installed. Install the bench host "
            "dependency first: pip install aioesphomeapi"
        )


def _read_secret_value(prompt: str, env_var: str | None) -> str:
    """Read a throwaway credential without echoing it.

    Order: explicit environment variable (for scripted bench runs with
    values generated at execution time), then interactive no-echo prompt.
    The value is returned to the caller and never printed or logged.
    """
    if env_var:
        from_env = os.environ.get(env_var)
        if from_env is not None:
            if not from_env:
                sys.exit(f"environment variable {env_var} is set but empty")
            return from_env
    value = getpass.getpass(f"{prompt} (input hidden, not logged): ")
    if not value:
        sys.exit("empty value refused — supply a throwaway bench value")
    return value


def _generate_noise_key() -> str:
    """Generate a fresh throwaway 32-byte PSK, base64-encoded."""
    return base64.b64encode(_secrets.token_bytes(32)).decode("ascii")


async def _connect(args: argparse.Namespace):
    """Connect to the device; plaintext when no key, noise when key given."""
    key: str | None = None
    if args.key_env and os.environ.get(args.key_env):
        key = os.environ[args.key_env]
    elif args.prompt_key:
        key = getpass.getpass("noise key (input hidden, not logged): ") or None
    client = aioesphomeapi.APIClient(args.host, args.port, password=None, noise_psk=key)
    await client.connect(login=True)
    return client


async def _fetch_diagnostics(client) -> dict[str, str]:
    entities, _services = await client.list_entities_services()
    keys: dict[int, str] = {}
    for entity in entities:
        object_id = getattr(entity, "object_id", "")
        if object_id in DIAGNOSTIC_OBJECT_IDS or object_id.startswith("bench_"):
            keys[entity.key] = object_id
    states: dict[str, str] = {}
    done = asyncio.Event()

    def on_state(state) -> None:
        object_id = keys.get(getattr(state, "key", -1))
        if object_id is None:
            return
        states[object_id] = str(getattr(state, "state", ""))
        if len(states) >= len(keys):
            done.set()

    client.subscribe_states(on_state)
    try:
        await asyncio.wait_for(done.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        pass  # print whatever arrived; missing entities show as absent
    return states


def _print_diagnostics(states: dict[str, str]) -> None:
    print("--- bench diagnostics (non-secret states only) ---")
    if not states:
        print("(no bench_* entity states received)")
    for object_id in sorted(states):
        print(f"{object_id:32s} {states[object_id]}")
    print("--------------------------------------------------")


async def _call_service(client, service_name: str, data: dict) -> None:
    _entities, services = await client.list_entities_services()
    for service in services:
        if service.name == service_name:
            client.execute_service(service, data)
            # Give the connection a moment to flush the request.
            await asyncio.sleep(1.0)
            return
    sys.exit(
        f"service {service_name!r} not found on the device — is the "
        "bench spike harness image flashed?"
    )


async def _press_button(client, object_id_fragment: str) -> None:
    entities, _services = await client.list_entities_services()
    for entity in entities:
        if type(entity).__name__ == "ButtonInfo" and object_id_fragment in getattr(
            entity, "object_id", ""
        ):
            client.button_command(entity.key)
            await asyncio.sleep(1.0)
            return
    sys.exit(f"button matching {object_id_fragment!r} not found on the device")


async def cmd_set_api_key(args: argparse.Namespace) -> None:
    key = _read_secret_value("throwaway noise key (base64, 32 bytes)", args.key_env)
    try:
        if len(base64.b64decode(key)) != 32:
            sys.exit("key must decode to exactly 32 bytes")
    except Exception:
        sys.exit("key is not valid base64")
    client = await _connect(args)
    try:
        ok = await client.noise_encryption_set_key(key.encode("ascii"))
    finally:
        await client.disconnect()
    if not ok:
        sys.exit("device rejected the set-key request (record as evidence)")
    print("set-key acknowledged by device (key value not logged).")
    print("Reconnect WITH the key to verify the encrypted session (V-01 step 5).")


async def cmd_set_ota_password(args: argparse.Namespace) -> None:
    secret_value = _read_secret_value("throwaway OTA password", args.value_env)
    client = await _connect(args)
    try:
        await _call_service(client, "bench_set_ota_password", {"value": secret_value})
        value_len = len(secret_value)
    finally:
        await client.disconnect()
    print(f"bench_set_ota_password called (value not logged, len={value_len}).")


async def cmd_set_ap_password(args: argparse.Namespace) -> None:
    secret_value = _read_secret_value("throwaway AP password", args.value_env)
    if len(secret_value) < 8:
        sys.exit("WPA2 requires >= 8 characters — supply a longer throwaway value")
    client = await _connect(args)
    try:
        await _call_service(client, "bench_set_ap_password", {"value": secret_value})
        value_len = len(secret_value)
    finally:
        await client.disconnect()
    print(f"bench_set_ap_password called (value not logged, len={value_len}).")


async def cmd_set_record(args: argparse.Namespace) -> None:
    client = await _connect(args)
    try:
        await _call_service(
            client,
            "bench_set_synthetic_record",
            {"uuid": args.uuid, "state": args.state},
        )
    finally:
        await client.disconnect()
    print(f"synthetic record written: uuid={args.uuid!r} state={args.state!r}")


async def cmd_clear_record(args: argparse.Namespace) -> None:
    client = await _connect(args)
    try:
        await _call_service(client, "bench_clear_synthetic_record", {})
    finally:
        await client.disconnect()
    print("synthetic record cleared.")


async def cmd_inspect(args: argparse.Namespace) -> None:
    client = await _connect(args)
    try:
        states = await _fetch_diagnostics(client)
    finally:
        await client.disconnect()
    _print_diagnostics(states)


async def cmd_reboot_test(args: argparse.Namespace) -> None:
    client = await _connect(args)
    try:
        await _press_button(client, "bench_restart")
    finally:
        await client.disconnect()
    print(f"restart requested; waiting {args.wait}s for reboot ...")
    await asyncio.sleep(args.wait)
    client = await _connect(args)
    try:
        states = await _fetch_diagnostics(client)
    finally:
        await client.disconnect()
    _print_diagnostics(states)


async def cmd_reset_test(args: argparse.Namespace) -> None:
    print(
        "WARNING: this presses the stock factory-reset button and ERASES\n"
        "the device's ENTIRE NVS partition (API key, saved WiFi, all bench\n"
        "globals). Procedure checks V-02 step 6 / V-07 leg 3 only."
    )
    answer = input(f"Type exactly {RESET_CONFIRMATION!r} to continue: ")
    if answer != RESET_CONFIRMATION:
        sys.exit("confirmation mismatch — aborted, nothing was done")
    client = await _connect(args)
    try:
        await _press_button(client, "bench_factory_reset")
    finally:
        await client.disconnect()
    print("factory reset requested. The device erases NVS and reboots.")
    print("Verify the post-reset state per the procedure (do not assume it).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", help="device IP or mDNS name")
    parser.add_argument("--port", type=int, default=6053, help="API port")
    parser.add_argument(
        "--key-env",
        default=None,
        help=(
            "name of an environment variable holding the throwaway noise "
            "key for this run (never a committed value)"
        ),
    )
    parser.add_argument(
        "--prompt-key",
        action="store_true",
        help="prompt (no echo) for the noise key to connect with",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("gen-key", help="generate a throwaway 32-byte base64 noise key")
    sub.add_parser("set-api-key", help="send the stock set-key request (V-01)")

    p = sub.add_parser("set-ota-password", help="apply a throwaway OTA password")
    p.add_argument(
        "--value-env",
        default=None,
        help="environment variable holding the throwaway value for this run",
    )
    p = sub.add_parser("set-ap-password", help="apply a throwaway AP password")
    p.add_argument("--value-env", default=None, help="as for set-ota-password")

    p = sub.add_parser("set-record", help="write the synthetic record (H-04)")
    p.add_argument("--uuid", required=True, help="clearly-synthetic bench value")
    p.add_argument(
        "--state",
        default="BENCH_SYNTHETIC",
        help="synthetic ownership-state marker (default: BENCH_SYNTHETIC)",
    )
    sub.add_parser("clear-record", help="clear the synthetic record")
    sub.add_parser("inspect", help="print non-secret diagnostics")

    p = sub.add_parser("reboot-test", help="restart, reconnect, re-inspect")
    p.add_argument("--wait", type=float, default=20.0, help="seconds to wait")

    sub.add_parser(
        "reset-test", help="stock factory reset (typed confirmation required)"
    )
    return parser


COMMANDS = {
    "set-api-key": cmd_set_api_key,
    "set-ota-password": cmd_set_ota_password,
    "set-ap-password": cmd_set_ap_password,
    "set-record": cmd_set_record,
    "clear-record": cmd_clear_record,
    "inspect": cmd_inspect,
    "reboot-test": cmd_reboot_test,
    "reset-test": cmd_reset_test,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "gen-key":
        # The ONE intended credential output: a fresh throwaway key the
        # operator records as bench evidence (procedure V-01 step 3).
        print(_generate_noise_key())
        return 0
    _require_aioesphomeapi()
    if not args.host:
        parser.error("--host is required for device commands")
    try:
        asyncio.run(COMMANDS[args.command](args))
    except (ConnectionError, OSError, TimeoutError) as exc:
        sys.exit(f"connection to {args.host} failed: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

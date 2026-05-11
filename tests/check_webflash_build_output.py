#!/usr/bin/env python3
"""Assert a built firmware filename matches config/webflash-builds.json.

Used by ``.github/workflows/firmware-build-release.yml`` after the rename
step to fail loudly if the WebFlash filename produced for a build differs
from what ``config/webflash-builds.json`` declares for the same product +
version + channel.

Lookup rule:

* Match a builds entry whose ``product_yaml`` basename (without ``.yaml``)
  equals the supplied ``--product``, *and* whose ``version`` and ``channel``
  match the supplied values exactly.
* If no entry matches (e.g. a dev/preview dispatch with version ``0.0.0-dev``
  or a product not in the WebFlash build matrix), exit 0 — there is nothing
  to assert against.
* If exactly one entry matches and its ``artifact_name`` equals the supplied
  ``--actual`` filename, exit 0.
* If exactly one entry matches and its ``artifact_name`` differs, exit 1.
* If more than one entry matches, exit 1 (ambiguous declaration).

This is intentionally conservative: it never fails on dev/preview dispatches
that legitimately use version/channel values not declared in the build
matrix. The only way to fail is to have a published build entry whose
declared ``artifact_name`` disagrees with what CI actually produced for the
matching version + channel.

Usage::

    python3 tests/check_webflash_build_output.py \\
        --product sense360-ceiling-poe-ventiq-roomiq \\
        --version 1.0.0 \\
        --channel stable \\
        --actual firmware-output/Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from product_name_mapper import generate_webflash_filename  # noqa: E402


def _matches(entry: dict, product: str, version: str, channel: str) -> bool:
    """Return True if ``entry`` covers the (product, version, channel) triple.

    A match is either:

    * the entry's ``product_yaml`` basename equals ``product`` directly
      (e.g. webflash-builds.json points at the canonical product YAML), or
    * the supplied ``product`` runs through ``product_name_mapper`` and
      produces the same WebFlash filename the entry declares
      (covers the case where webflash-builds.json points at a thin
      ``products/webflash/`` wrapper but the build matrix uses the
      canonical ``sense360-`` stem).
    """
    if entry.get("version") != version or entry.get("channel") != channel:
        return False
    yaml_path = entry.get("product_yaml", "")
    if Path(yaml_path).stem == product:
        return True
    return generate_webflash_filename(product, version, channel) == entry.get(
        "artifact_name"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--product", required=True, help="matrix.product (basename of product YAML)")
    parser.add_argument("--version", required=True, help="version emitted into filename")
    parser.add_argument("--channel", required=True, help="channel emitted into filename")
    parser.add_argument(
        "--actual",
        required=True,
        help="path or filename of the renamed binary (basename is what is checked)",
    )
    args = parser.parse_args()

    if not BUILDS_PATH.is_file():
        print(f"error: {BUILDS_PATH} does not exist", file=sys.stderr)
        return 1

    try:
        builds = json.loads(BUILDS_PATH.read_text()).get("builds", [])
    except json.JSONDecodeError as exc:
        print(f"error: cannot parse {BUILDS_PATH}: {exc}", file=sys.stderr)
        return 1

    matches = [b for b in builds if _matches(b, args.product, args.version, args.channel)]

    if not matches:
        print(
            "no webflash-builds.json entry for "
            f"product={args.product} version={args.version} channel={args.channel}; "
            "skipping build-output assertion (dev/preview dispatch or non-WebFlash product)"
        )
        return 0

    if len(matches) > 1:
        print(
            f"error: more than one webflash-builds.json entry matches "
            f"product={args.product} version={args.version} channel={args.channel}",
            file=sys.stderr,
        )
        return 1

    expected = matches[0]["artifact_name"]
    actual_basename = Path(args.actual).name
    if actual_basename != expected:
        print(
            f"error: build output filename mismatch\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual_basename}",
            file=sys.stderr,
        )
        return 1

    print(
        f"ok: build output {actual_basename} matches "
        f"webflash-builds.json entry for {args.product} v{args.version} {args.channel}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

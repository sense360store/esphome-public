#!/usr/bin/env python3
"""Generate customer-docs content blocks (SENSE360-CUSTOMER-DOCS-001 Phase 2).

Every factual block on a customer page is generated from declared truth,
never hand-authored. This generator reads the in-repo sources and writes
markdown includes under ``site/generated/`` for the mkdocs snippets
extension (base_path: site/generated):

  room-<room>-box-contents.md   from config/webflash-preset-snapshot.json
                                (component list per installer preset) +
                                config/hardware-catalog.json (what each
                                board does, customer wording)
  room-<room>-flash-steps.md    from the same snapshot (the preset name a
                                room page may instruct customers to pick)
  sensor-glossary.md            from config/hardware-catalog.json
  led-behaviour.md              from packages/features/led_framework.yaml
                                (the named customer controls, paired with
                                a wording map that hard-fails on any new
                                or renamed control)

Each block carries an HTML provenance comment naming its sources (and the
mirror's upstream SHA where applicable). ``--check`` regenerates in
memory and exits non-zero on drift — wired into the docs-site CI lane and
tests/test_customer_docs_site.py, so a stale block fails CI. Inputs are
all in-repo, which is what makes the hard freshness gate possible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = REPO_ROOT / "config" / "webflash-preset-snapshot.json"
HARDWARE = REPO_ROOT / "config" / "hardware-catalog.json"
LED_FRAMEWORK = REPO_ROOT / "packages" / "features" / "led_framework.yaml"
OUT_DIR = REPO_ROOT / "site" / "generated"

# Customer wording per LED framework control, keyed by entity id so a
# framework rename or a new control fails the generator until wording is
# added deliberately. Entity platforms walked: light, switch, select,
# number, button (named text_sensor diagnostics are technical surface and
# excluded from the customer table).
LED_CONTROL_WORDING = {
    "led_ring": "The ring itself — turn it on or off, set colour and brightness like any light.",
    "s360_led_night_mode": "Dims the ring for night. Turn it on manually or let the automatic setting do it.",
    "s360_led_night_behaviour": "What night mode does when it activates: dim the ring or switch it off entirely.",
    "s360_led_status_indicator": "Whether the ring briefly shows device status events as coloured overlays.",
    "s360_led_darkness_threshold": "How dark the room must be before automatic night mode considers it night.",
    "s360_led_identify": "Flashes the ring so you can tell which device you are looking at.",
}

# Customer wording per board SKU. Keyed by SKU so a catalog rename or a
# new board forces a deliberate edit here; the catalog stays the identity
# authority and the guard below fails on an unknown SKU.
BOARD_CUSTOMER_WORDING = {
    "S360-100": "The hub. ESP32-S3 brain with connectors for every module.",
    "S360-200": "Room sensing: presence, light, temperature, humidity, pressure.",
    "S360-210": "Air quality: CO₂, VOC and NOx trends, gas sensing.",
    "S360-211": "Bathroom air quality: VOC and NOx trends for ventilation decisions.",
    "S360-300": "A ring of lights for glanceable room status.",
    "S360-400": "Power from a mains supply.",
    "S360-410": "Power over your network cable. No wall adapter needed.",
}

# Customer glossary wording per board: what the sensors mean, no part
# numbers in the lead sentence (part identities stay in the technical
# reference; the catalog remains the identity authority).
GLOSSARY = (
    ("S360-100", "Hub", "Runs the firmware, talks to Home Assistant over your network, and connects every module."),
    ("S360-200", "Room sensing", "Detects whether the room is occupied (warm-body and optional radar sensing) and measures light level, temperature, humidity and air pressure."),
    ("S360-210", "Air quality", "Tracks carbon dioxide, airborne chemical (VOC and NOx) trends and gas readings so Home Assistant can drive ventilation."),
    ("S360-211", "Bathroom air quality", "Tracks airborne chemical (VOC and NOx) trends sized for bathrooms, alongside the room sensing that drives fan decisions."),
    ("S360-300", "Light ring", "Shows room status at a glance with a ring of lights."),
    ("S360-400", "Mains power", "Powers the hub from a mains supply."),
    ("S360-410", "Network power", "Powers the hub over the same cable as your network (PoE)."),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _led_controls() -> list[tuple[str, str]]:
    """(entity id, customer name) for every named LED framework control."""
    import yaml

    # Isolated loader subclass: registering ESPHome tag constructors on
    # the global SafeLoader would clobber the constructors other tools
    # and tests register when they share a process.
    class _LedLoader(yaml.SafeLoader):
        pass

    def ctor(loader, node):
        return None

    for tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
        yaml.add_constructor(tag, ctor, Loader=_LedLoader)
    doc = yaml.load(LED_FRAMEWORK.read_text(encoding="utf-8"), Loader=_LedLoader)
    controls = []
    for platform_key in ("light", "switch", "select", "number", "button"):
        for entry in doc.get(platform_key) or []:
            if isinstance(entry, dict) and entry.get("id") and entry.get("name"):
                controls.append((entry["id"], str(entry["name"])))
    return controls


def _provenance(*sources: str) -> str:
    lines = "\n".join(f"  {s}" for s in sources)
    return (
        "<!-- GENERATED by scripts/generate_customer_docs_blocks.py — do not\n"
        "hand-edit. Sources:\n" + lines + "\n"
        "Regenerate: python3 scripts/generate_customer_docs_blocks.py -->\n"
    )


def build_blocks() -> dict[str, str]:
    snapshot = _load(SNAPSHOT)
    hardware = _load(HARDWARE)
    catalog_names = {
        e["sku"]: e.get("friendly_name") or e.get("name")
        for e in hardware.get("items") or []
        if isinstance(e, dict) and e.get("sku")
    }
    snap_prov = (
        f"config/webflash-preset-snapshot.json (mirror of "
        f"{snapshot['provenance']['source_repo']} @ "
        f"{snapshot['provenance']['source_sha']})"
    )
    blocks: dict[str, str] = {}
    for preset in snapshot["presets"]:
        room = preset["room_label"].lower()
        rows = []
        for comp in preset.get("components") or []:
            sku = comp["sku"]
            wording = BOARD_CUSTOMER_WORDING.get(sku)
            if wording is None:
                raise SystemExit(
                    f"no customer wording for board {sku} — add it to "
                    "BOARD_CUSTOMER_WORDING (catalog identity is unchanged)"
                )
            label = comp.get("label") or catalog_names.get(sku, sku)
            rows.append(f"| {label} | {wording} |")
        blocks[f"room-{room}-box-contents.md"] = (
            _provenance(snap_prov, "config/hardware-catalog.json")
            + "\n| Board | What it does |\n|---|---|\n"
            + "\n".join(rows)
            + "\n"
        )
        blocks[f"room-{room}-flash-steps.md"] = (
            _provenance(snap_prov)
            + "\n"
            + "1. Connect the hub over USB-C and open the installer.\n"
            + f"2. Choose the **{preset['room_label']}** setup when asked "
            + "for your room.\n"
            + "3. Follow the on-screen steps; the installer verifies the "
            + "firmware and flashes the device.\n"
        )
    glossary_rows = []
    for sku, term, meaning in GLOSSARY:
        name = catalog_names.get(sku)
        if not name:
            raise SystemExit(f"glossary references unknown board {sku}")
        glossary_rows.append(f"| {name} | {term} | {meaning} |")
    blocks["sensor-glossary.md"] = (
        _provenance("config/hardware-catalog.json")
        + "\n| Board | In plain terms | What it does for you |\n|---|---|---|\n"
        + "\n".join(glossary_rows)
        + "\n"
    )
    led_rows = []
    for entity_id, name in _led_controls():
        wording = LED_CONTROL_WORDING.get(entity_id)
        if wording is None:
            raise SystemExit(
                f"no customer wording for LED control {entity_id!r} "
                f"({name!r}) — add it to LED_CONTROL_WORDING"
            )
        led_rows.append(f"| {name} | {wording} |")
    if not led_rows:
        raise SystemExit("no named LED controls found in the framework")
    blocks["led-behaviour.md"] = (
        _provenance("packages/features/led_framework.yaml")
        + "\n| Control | What it does |\n|---|---|\n"
        + "\n".join(led_rows)
        + "\n"
    )
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    blocks = build_blocks()
    stale = []
    for name, text in blocks.items():
        path = OUT_DIR / name
        if args.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote site/generated/{name}")
    if stale:
        print(
            "stale customer-docs blocks: " + ", ".join(stale)
            + " — regenerate with python3 scripts/generate_customer_docs_blocks.py",
            file=sys.stderr,
        )
        return 1
    if args.check:
        print(f"Customer-docs blocks are fresh ({len(blocks)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
